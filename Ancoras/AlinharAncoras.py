#MenuTitle: Alinhar Âncoras
# -*- coding: utf-8 -*-

__doc__="""
Alinha Âncoras em posição Y 
conforme definido 
"""

import vanilla

class AlinharAncoras(object):
    def __init__(self):
        Glyphs.clearLog()
        
        self.font = Glyphs.font
        if not self.font:
            print("⚠️ Nenhuma fonte aberta.")
            return

        # Dimensões da janela ajustadas
        self.w = vanilla.FloatingWindow((380, 560), "Alinhar Âncoras")
        
        y = 15
        # 1. Caixa Informativa
        self.w.box_info = vanilla.Box((15, y, -15, 45))
        self.w.box_info.lbl = vanilla.TextBox(
            (10, 5, -10, 35),
            "O ajuste será aplicado \nem glifo(s) selecionado(s) da master ativa.",
            sizeStyle="small"
        )
        
        # 2. SEÇÃO TOP ANCHORS
        y += 55
        self.w.box_top = vanilla.Box((15, y, -15, 175))
        
        top_y = 10
        self.w.box_top.lbl_title = vanilla.TextBox((10, top_y, 200, 20), "Âncoras de topo", sizeStyle="small")
        
        top_y += 22
        self.w.box_top.lbl_y = vanilla.TextBox((10, top_y+3, 60, 20), "Altura Y:")
        # Campo de Texto Y do Topo POSICIONADO DENTRO da box_top
        self.w.box_top.input_top_y = vanilla.EditText((75, top_y, 80, 22), "700")
        
        # Presets em DUAS LINHAS
        top_y += 30
        self.w.box_top.btn_xheight = vanilla.Button((10, top_y, 160, 20), "x-Height", sizeStyle="small", callback=self.set_preset_xheight)
        self.w.box_top.btn_sc = vanilla.Button((180, top_y, 160, 20), "Small Caps", sizeStyle="small", callback=self.set_preset_sc)
        
        top_y += 24
        self.w.box_top.btn_capheight = vanilla.Button((10, top_y, 160, 20), "Cap Height", sizeStyle="small", callback=self.set_preset_capheight)
        self.w.box_top.btn_ascender = vanilla.Button((180, top_y, 160, 20), "Ascender", sizeStyle="small", callback=self.set_preset_ascender)
        
        # Checkboxes de Top
        top_y += 32
        self.w.box_top.chk_top = vanilla.CheckBox((10, top_y, 60, 20), "top", value=True)
        self.w.box_top.chk_top_underscore = vanilla.CheckBox((80, top_y, 65, 20), "_top", value=True)
        self.w.box_top.chk_topleft = vanilla.CheckBox((155, top_y, 75, 20), "topleft", value=False)
        self.w.box_top.chk_topright = vanilla.CheckBox((235, top_y, 80, 20), "topright", value=False)
        
        # 3. SEÇÃO BOTTOM ANCHORS
        y += 185
        self.w.box_bottom = vanilla.Box((15, y, -15, 105))
        
        bot_y = 10
        self.w.box_bottom.lbl_title = vanilla.TextBox((10, bot_y, 200, 20), "Âncoras de base", sizeStyle="small")
        
        bot_y += 22
        self.w.box_bottom.lbl_y = vanilla.TextBox((10, bot_y+3, 60, 20), "Altura Y:")
        self.w.box_bottom.input_bottom_y = vanilla.EditText((75, bot_y, 80, 22), "0")
        
        bot_y += 30
        self.w.box_bottom.chk_bottom = vanilla.CheckBox((10, bot_y, 75, 20), "bottom", value=False)
        self.w.box_bottom.chk_bottom_underscore = vanilla.CheckBox((90, bot_y, 80, 20), "_bottom", value=False)
        self.w.box_bottom.chk_cedilla = vanilla.CheckBox((175, bot_y, 65, 20), "cedilla", value=False)
        self.w.box_bottom.chk_cedilla_underscore = vanilla.CheckBox((245, bot_y, 75, 20), "_cedilla", value=False)
        
        # 4. SEÇÃO CUSTOM ANCHORS
        y += 115
        self.w.box_custom = vanilla.Box((15, y, -15, 100))
        
        cust_y = 10
        self.w.box_custom.chk_custom = vanilla.CheckBox((10, cust_y, 130, 20), "Custom 1:", value=False)
        self.w.box_custom.input_custom_name = vanilla.EditText((145, cust_y, 120, 22), placeholder="ogonek")
        self.w.box_custom.lbl_y1 = vanilla.TextBox((270, cust_y+3, 25, 20), "Y:", sizeStyle="small")
        self.w.box_custom.input_custom_y = vanilla.EditText((290, cust_y, 50, 22), "0")
        
        cust_y += 32
        self.w.box_custom.chk_custom2 = vanilla.CheckBox((10, cust_y, 130, 20), "Custom 2:", value=False)
        self.w.box_custom.input_custom_name2 = vanilla.EditText((145, cust_y, 120, 22), placeholder="ex: center")
        self.w.box_custom.lbl_y2 = vanilla.TextBox((270, cust_y+3, 25, 20), "Y:", sizeStyle="small")
        self.w.box_custom.input_custom_y2 = vanilla.EditText((290, cust_y, 50, 22), "0")

        # 5. BOTÃO PRINCIPAL
        y += 115
        self.w.btn_run = vanilla.Button((15, y, -15, 30), "Alinhar Âncoras", callback=self.run)
        
        self.w.open()

    # Callbacks de Presets
    def set_preset_xheight(self, sender):
        master = self.font.selectedFontMaster
        if master:
            self.w.box_top.input_top_y.set(str(int(master.xHeight)))

    def set_preset_sc(self, sender):
        master = self.font.selectedFontMaster
        if not master:
            return

        sc_value = None

        for metric in self.font.metrics:
            metric_name = (metric.name or "").lower()
            metric_filter = str(metric.filter) if hasattr(metric, "filter") and metric.filter else ""

            if "small" in metric_name or "sc" in metric_name or "case == 3" in metric_filter or "smallcap" in metric_filter:
                if metric.id in master.metrics:
                    sc_value = master.metrics[metric.id].position
                    break

        if sc_value is None and "smallCapHeight" in master.customParameters:
            sc_value = master.customParameters["smallCapHeight"]

        if sc_value is not None:
            self.w.box_top.input_top_y.set(str(int(sc_value)))
            print(f"Métrica Small Caps carregada: Y = {int(sc_value)}")
        else:
            print("⚠️ Nenhuma métrica de Small Caps encontrada em Font Info > Metrics para esta master.")

    def set_preset_capheight(self, sender):
        master = self.font.selectedFontMaster
        if master:
            self.w.box_top.input_top_y.set(str(int(master.capHeight)))

    def set_preset_ascender(self, sender):
        master = self.font.selectedFontMaster
        if master:
            self.w.box_top.input_top_y.set(str(int(master.ascender)))

    def run(self, sender):
        selected_layers = self.font.selectedLayers
        if not selected_layers:
            print("⚠️ Nenhum glifo selecionado.")
            return

        ancoras_alvo = {}

        # Top Anchors
        try:
            target_top_y = float(self.w.box_top.input_top_y.get())
            if self.w.box_top.chk_top.get(): ancoras_alvo["top"] = target_top_y
            if self.w.box_top.chk_top_underscore.get(): ancoras_alvo["_top"] = target_top_y
            if self.w.box_top.chk_topleft.get(): ancoras_alvo["topleft"] = target_top_y
            if self.w.box_top.chk_topright.get(): ancoras_alvo["topright"] = target_top_y
        except ValueError:
            print("❌ Erro: O valor de Y das Âncoras de topo precisa ser um número válido.")
            return

        # Bottom Anchors
        try:
            target_bottom_y = float(self.w.box_bottom.input_bottom_y.get())
            if self.w.box_bottom.chk_bottom.get(): ancoras_alvo["bottom"] = target_bottom_y
            if self.w.box_bottom.chk_bottom_underscore.get(): ancoras_alvo["_bottom"] = target_bottom_y
            if self.w.box_bottom.chk_cedilla.get(): ancoras_alvo["cedilla"] = target_bottom_y
            if self.w.box_bottom.chk_cedilla_underscore.get(): ancoras_alvo["_cedilla"] = target_bottom_y
        except ValueError:
            print("❌ Erro: O valor de Y das Âncoras de base precisa ser um número válido.")
            return

        # Custom Anchors
        if self.w.box_custom.chk_custom.get():
            custom_name = self.w.box_custom.input_custom_name.get().strip()
            if custom_name:
                try:
                    ancoras_alvo[custom_name] = float(self.w.box_custom.input_custom_y.get())
                except ValueError:
                    print("❌ Erro: O valor Y da Âncora Custom 1 precisa ser um número válido.")
                    return

        if self.w.box_custom.chk_custom2.get():
            custom_name2 = self.w.box_custom.input_custom_name2.get().strip()
            if custom_name2:
                try:
                    ancoras_alvo[custom_name2] = float(self.w.box_custom.input_custom_y2.get())
                except ValueError:
                    print("❌ Erro: O valor Y da Âncora Custom 2 precisa ser um número válido.")
                    return

        if not ancoras_alvo:
            print("⚠️ Nenhuma âncora foi marcada na interface para ser ajustada.")
            return

        active_master = self.font.selectedFontMaster
        print(f"Alinhando âncoras na Master: {active_master.name}...")

        self.font.disableUpdateInterface()
        modificados = 0

        try:
            for layer in selected_layers:
                glyph = layer.parent
                for anchor in layer.anchors:
                    if anchor.name in ancoras_alvo:
                        target_y = ancoras_alvo[anchor.name]
                        if anchor.position.y != target_y:
                            anchor.position = (anchor.position.x, target_y)
                            modificados += 1
                            print(f"  ↳ {glyph.name}: '{anchor.name}' -> Y = {target_y}")
        finally:
            self.font.enableUpdateInterface()

        print(f"\nConcluído! Total de {modificados} âncora(s) ajustada(s).")

AlinharAncoras()
