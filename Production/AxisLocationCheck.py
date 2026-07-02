# MenuTitle: Editor de Axis Location
# encoding: utf-8

__doc__ = """
Mostra os Axis Location de Masters
ou instâncias e permite a edição
do valor de cada eixo em uma seleção
de vários itens. 
(Ex: Alterar todos os itálicos)
"""

from AppKit import NSApp, NSTableView
import vanilla


def collect_tableviews(view, result):
    if isinstance(view, NSTableView):
        result.append(view)
    for sub in view.subviews():
        collect_tableviews(sub, result)


def get_selected_items(font):
    """Encontra as linhas selecionadas tanto na tabela de Masters quanto de Exports/Instâncias."""
    candidatas = []
    for window in NSApp.windows():
        title = window.title() or ""
        if "Font Info" in title or font.familyName in title:
            candidatas.append(window)

    if not candidatas:
        candidatas = [w for w in NSApp.windows() if w.isVisible()]

    selected_masters = []
    selected_instances = []

    for window in candidatas:
        tableviews = []
        collect_tableviews(window.contentView(), tableviews)
        for tv in tableviews:
            row_count = tv.numberOfRows()
            indices = list(tv.selectedRowIndexes())
            if not indices:
                continue
                
            # Verifica se a tabela corresponde às Masters
            if row_count == len(font.masters):
                # Evita duplicar se o mesmo item bater por coincidência de tamanho
                items = [font.masters[i] for i in indices if i < len(font.masters)]
                if items and items[0] not in selected_masters:
                    selected_masters = items
            
            # Verifica se a tabela corresponde às Instâncias
            if row_count == len(font.instances):
                items = [font.instances[i] for i in indices if i < len(font.instances)]
                if items and items[0] not in selected_instances:
                    selected_instances = items

    return selected_masters, selected_instances


class AxisLocationEditor(object):

    def __init__(self):
        self.font = Glyphs.font
        if self.font is None:
            Glyphs.showNotification("Axis Location Editor", "Nenhuma fonte aberta.")
            return

        self.selected_masters, self.selected_instances = get_selected_items(self.font)
        
        if not self.selected_masters and not self.selected_instances:
            Glyphs.showNotification(
                "Axis Location Editor",
                "Nenhum item selecionado. Clique nas linhas em Font Info > Masters ou Exports e rode novamente."
            )
            return

        self.axis_names = [axis.name for axis in self.font.axes]
        self.values = []
        self.display_items = []

        # Processa Masters selecionadas
        for master in self.selected_masters:
            current = master.customParameters["Axis Location"] or []
            lookup = {entry.get("Axis"): entry.get("Location") for entry in current}
            self.values.append({axis_name: lookup.get(axis_name, "") for axis_name in self.axis_names})
            self.display_items.append({"object": master, "type": "Master", "name": master.name})

        # Processa Instâncias selecionadas
        for inst in self.selected_instances:
            current = inst.customParameters["Axis Location"] or []
            lookup = {entry.get("Axis"): entry.get("Location") for entry in current}
            self.values.append({axis_name: lookup.get(axis_name, "") for axis_name in self.axis_names})
            self.display_items.append({"object": inst, "type": "Instância", "name": inst.name})

        self.current_axis_index = 0

        total_items = len(self.display_items)
        height = 140 + 22 * total_items
        self.w = vanilla.FloatingWindow((440, min(max(height, 240), 580)),
                                         "Editar Axis Location (%d itens selecionados)" % total_items)

        y = 10
        self.w.axisLabel = vanilla.TextBox((10, y + 2, 90, 20), "Eixo Ativo:")
        self.w.axisPopup = vanilla.PopUpButton((110, y, 180, 20), self.axis_names,
                                               callback=self.axisChangedCallback)

        columns = [
            dict(title="Tipo", key="Tipo", editable=False, width=70),
            dict(title="Nome do Item", key="Nome", editable=False, width=220),
            dict(title="Valor", key="Valor", editable=True),
        ]
        self.w.list = vanilla.List((10, 40, -10, -80), self.buildRows(),
                                    columnDescriptions=columns)

        by = -65
        self.w.bulkValue = vanilla.EditText((10, by, 100, 20), "")
        self.w.bulkApply = vanilla.Button((120, by, 140, 20), "Aplicar a todos",
                                           callback=self.bulkApplyCallback)

        self.w.saveButton = vanilla.Button((-140, -35, -10, 20), "Salvar", callback=self.saveCallback)
        self.w.cancelButton = vanilla.Button((-260, -35, -150, 20), "Cancelar", callback=self.cancelCallback)

        self.w.open()

    def buildRows(self):
        axis_name = self.axis_names[self.current_axis_index]
        rows = []
        for item, vals in zip(self.display_items, self.values):
            rows.append({
                "Tipo": item["type"],
                "Nome": item["name"],
                "Valor": str(vals[axis_name]) if vals[axis_name] != "" else ""
            })
        return rows

    def storeCurrentColumn(self):
        """Salva temporariamente na memória as edições feitas na tabela."""
        axis_name = self.axis_names[self.current_axis_index]
        data = self.w.list.get()
        for vals, row in zip(self.values, data):
            vals[axis_name] = row.get("Valor", "")

    def axisChangedCallback(self, sender):
        self.storeCurrentColumn()
        self.current_axis_index = sender.get()
        self.w.list.set(self.buildRows())

    def bulkApplyCallback(self, sender):
        value = self.w.bulkValue.get()
        if value == "":
            return
        
        axis_name = self.axis_names[self.current_axis_index]
        for vals in self.values:
            vals[axis_name] = value
            
        self.w.list.set(self.buildRows())

    def saveCallback(self, sender):
        self.storeCurrentColumn()
        
        self.font.disableUpdateInterface()
        atualizados = 0
        try:
            for item, vals in zip(self.display_items, self.values):
                obj = item["object"]
                current = obj.customParameters["Axis Location"] or []
                lookup = {entry.get("Axis"): entry for entry in current}

                novo = []
                for axis_name in self.axis_names:
                    raw_value = vals.get(axis_name, "")
                    try:
                        valor = float(raw_value)
                        if valor.is_integer():
                            valor = int(valor)
                    except (TypeError, ValueError):
                        # Mantém o valor original se o campo for inválido ou vazio
                        valor = lookup.get(axis_name, {}).get("Location", 0)
                    
                    novo.append({"Axis": axis_name, "Location": valor})

                obj.customParameters["Axis Location"] = novo
                atualizados += 1
        except Exception as e:
            print("Erro ao aplicar Axis Location: %s" % str(e))
        finally:
            self.font.enableUpdateInterface()

        Glyphs.showNotification("Axis Location Editor",
                                 "%d item(ns) atualizado(s) com sucesso." % atualizados)
        self.w.close()

    def cancelCallback(self, sender):
        self.w.close()


AxisLocationEditor()