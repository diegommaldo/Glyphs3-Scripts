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
                
            if row_count == len(font.masters):
                items = [font.masters[i] for i in indices if i < len(font.masters)]
                if items and items[0] not in selected_masters:
                    selected_masters = items
            
            if row_count == len(font.instances):
                items = [font.instances[i] for i in indices if i < len(font.instances)]
                if items and items[0] not in selected_instances:
                    selected_instances = items

    return selected_masters, selected_instances


class AxisLocationMatrixEditor(object):

    def __init__(self):
        self.font = Glyphs.font
        if self.font is None:
            Glyphs.showNotification("Axis Location Matrix", "Nenhuma fonte aberta.")
            return

        self.selected_masters, self.selected_instances = get_selected_items(self.font)
        
        num_m = len(self.selected_masters)
        num_i = len(self.selected_instances)

        if num_m == 0 and num_i == 0:
            Glyphs.showNotification(
                "Axis Location Matrix",
                "Nenhum item selecionado. Clique nas linhas em Font Info > Masters ou Exports e rode novamente."
            )
            return

        self.axis_names = [axis.name for axis in self.font.axes]
        self.table_data = []

        # Processa Masters selecionadas
        for master in self.selected_masters:
            current = master.customParameters["Axis Location"] or []
            lookup = {entry.get("Axis"): entry.get("Location") for entry in current}
            
            row = {"Tipo": "Master", "Nome": master.name, "_object": master}
            for axis_name in self.axis_names:
                val = lookup.get(axis_name, "")
                row[axis_name] = str(val) if val != "" else ""
            self.table_data.append(row)

        # Processa Instâncias selecionadas
        for inst in self.selected_instances:
            current = inst.customParameters["Axis Location"] or []
            lookup = {entry.get("Axis"): entry.get("Location") for entry in current}
            
            row = {"Tipo": "Instância", "Nome": inst.name, "_object": inst}
            for axis_name in self.axis_names:
                val = lookup.get(axis_name, "")
                row[axis_name] = str(val) if val != "" else ""
            self.table_data.append(row)

        # Cálculo responsivo inicial do tamanho
        col_tipo_w = 60
        col_nome_w = 160
        col_eixo_w = 70
        
        init_width = col_tipo_w + col_nome_w + (col_eixo_w * len(self.axis_names)) + 20
        init_width = max(init_width, 480) 
        
        init_height = 15 + (22 * len(self.table_data)) + 95
        init_height = min(max(init_height, 220), 750)

        # Geração inteligente do título ocultando valores zerados
        partes_titulo = []
        if num_m > 0:
            partes_titulo.append("%d Master(s)" % num_m)
        if num_i > 0:
            partes_titulo.append("%d Instância(s)" % num_i)
        
        window_title = "Matriz Axis Location (%s selecionada(s))" % " / ".join(partes_titulo)
        
        # Criando a janela flutuante com limites mínimos e máximos para habilitar o redimensionamento nativo do macOS
        self.w = vanilla.FloatingWindow(
            (init_width, init_height), 
            window_title,
            minSize=(480, 220),         # Impede o usuário de esmagar a interface além do limite funcional
            maxSize=(1800, 1200)        # Limite máximo seguro de expansão da tela
        )

        # Definição dinâmica das colunas da matriz
        columns = [
            dict(title="Tipo", key="Tipo", editable=False, width=col_tipo_w),
            dict(title="Nome do Item", key="Nome", editable=False, width=col_nome_w),
        ]
        for axis_name in self.axis_names:
            columns.append(dict(title=axis_name, key=axis_name, editable=True, width=col_eixo_w))

        # A tabela usa índices negativos (-10, -80) para grudar elasticamente nas bordas direita e inferior da janela
        self.w.list = vanilla.List((10, 10, -10, -80), self.table_data, columnDescriptions=columns)

        # Controles de aplicação em lote (Bulk Apply) ancorados dinamicamente na parte inferior
        by = -65
        self.w.bulkLabel = vanilla.TextBox((10, by + 2, 50, 20), "Inserir:")
        self.w.bulkValue = vanilla.EditText((65, by, 50, 20), "")
        self.w.bulkAxisLabel = vanilla.TextBox((125, by + 2, 50, 20), "no eixo:")
        self.w.bulkAxisPopup = vanilla.PopUpButton((180, by, 110, 20), self.axis_names)
        self.w.bulkApply = vanilla.Button((300, by, 110, 20), "Aplicar a todos", callback=self.bulkApplyCallback)

        # Botões de Ação ancorados à direita e abaixo usando coordenadas relativas negativas
        self.w.saveButton = vanilla.Button((-135, -35, -10, 20), "Salvar", callback=self.saveCallback)
        self.w.cancelButton = vanilla.Button((-255, -35, -145, 20), "Cancelar", callback=self.cancelCallback)

        self.w.open()

    def bulkApplyCallback(self, sender):
        value = self.w.bulkValue.get()
        if value == "":
            return
        
        axis_index = self.w.bulkAxisPopup.get()
        axis_name = self.axis_names[axis_index]
        
        current_data = self.w.list.get()
        for row in current_data:
            row[axis_name] = value
            
        self.w.list.set(current_data)

    def saveCallback(self, sender):
        final_data = self.w.list.get()
        
        self.font.disableUpdateInterface()
        atualizados = 0
        try:
            for row in final_data:
                obj = row.get("_object")
                if not obj:
                    continue
                
                current = obj.customParameters["Axis Location"] or []
                lookup = {entry.get("Axis"): entry for entry in current}

                novo = []
                for axis_name in self.axis_names:
                    raw_value = row.get(axis_name, "")
                    try:
                        valor = float(raw_value)
                        if valor.is_integer():
                            valor = int(valor)
                    except (TypeError, ValueError):
                        # Mantém o valor original se o campo estiver vazio ou inválido
                        valor = lookup.get(axis_name, {}).get("Location", 0)
                    
                    novo.append({"Axis": axis_name, "Location": valor})

                obj.customParameters["Axis Location"] = novo
                atualizados += 1
        except Exception as e:
            print("Erro ao salvar a matriz de Axis Location: %s" % str(e))
        finally:
            self.font.enableUpdateInterface()

        Glyphs.showNotification("Axis Location Matrix", 
                                 "%d item(ns) gravado(s) com sucesso." % atualizados)
        self.w.close()

    def cancelCallback(self, sender):
        self.w.close()


AxisLocationMatrixEditor()
