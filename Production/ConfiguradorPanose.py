# MenuTitle: Configurador PANOSE (instâncias)
# -*- coding: utf-8 -*-

__doc__="""
Adiciona o Custom Parameter PANOSE
nas instâncias, detecta automaticamente
pesos, largura e inclinação.
"""

import vanilla
from GlyphsApp import Glyphs

class PanoseConfigurator(object):
    def __init__(self):
        # Mapeamentos oficiais do PANOSE 1.0 (Text/Display)
        self.panose_options = {
            "Family Kind": ["0-Any", "1-No Fit", "2-Text and Display", "3-Script", "4-Decorative", "5-Pictorial"],
            "Serif Style": ["0-Any", "1-No Fit", "2-Cove", "3-Thin", "4-Square", "5-Square Cove", "6-Flat", "7-Double Cove", "8-Nominal", "9-Normal Sans", "10-Obtuse Cove", "11-Obtuse Sans", "12-Square Sans", "13-Lobated", "14-Flare", "15-Rounded"],
            "Weight": ["0-Any", "1-No Fit", "2-Very Light", "3-Light", "4-Thin", "5-Book", "6-Medium", "7-Demi", "8-Bold", "9-Heavy", "10-Black", "11-Extra Black"],
            "Proportion": ["0-Any", "1-No Fit", "2-Old Style", "3-Modern", "4-Even Width", "5-Expanded", "6-Condensed", "7-Very Expanded", "8-Very Condensed", "9-Monospaced"],
            "Contrast": ["0-Any", "1-No Fit", "2-None", "3-Very Low", "4-Low", "5-Medium Low", "6-Medium", "7-Medium High", "8-High", "9-Very High"],
            "Stroke Variation": ["0-Any", "1-No Fit", "2-No Variation", "3-Gradual/Diagonal", "4-Gradual/Transitional", "5-Gradual/Vertical", "6-Gradual/Horizontal", "7-Rapid/Vertical", "8-Rapid/Horizontal", "9-Instant/Vertical"],
            "Arm Style": ["0-Any", "1-No Fit", "2-Straight Arms/Horizontal", "3-Straight Arms/Wedge", "4-Straight Arms/Vertical", "5-Straight Arms/Single Notch", "6-Straight Arms/Double Notch", "7-Non-Straight/Horizontal", "8-Non-Straight/Wedge", "9-Non-Straight/Vertical", "10-Non-Straight/Single Notch", "11-Non-Straight/Double Notch"],
            "Letterform": ["0-Any", "1-No Fit", "2-Normal/Contact", "3-Normal/Weighted", "4-Normal/Boxed", "5-Normal/Flattened", "6-Normal/Rounded", "7-Normal/Off Center", "8-Normal/Square", "9-Oblique/Contact", "10-Oblique/Weighted", "11-Oblique/Boxed", "12-Oblique/Flattened", "13-Oblique/Rounded", "14-Oblique/Off Center", "15-Oblique/Square"],
            "Midline": ["0-Any", "1-No Fit", "2-Standard/Trimmed", "3-Standard/Pointed", "4-Standard/Serifed", "5-High/Trimmed", "6-High/Pointed", "7-High/Serifed", "8-Constant/Trimmed", "9-Constant/Pointed", "10-Constant/Serifed", "11-Low/Trimmed", "12-Low/Pointed", "13-Low/Serifed"],
            "X-Height": ["0-Any", "1-No Fit", "2-Constant/Small", "3-Constant/Standard", "4-Constant/Large", "5-Ductil/Small", "6-Ductil/Standard", "7-Ductil/Large"]
        }
        
        self.explicacoes_pt = {
            "Family Kind": "TIPO DE FAMÍLIA:\nDefine o gênero geral do design. Geralmente '2-Text and Display' para alfabetos latinos convencionais.",
            "Serif Style": "ESTILOS DA SERIFA:\nDescreve a geometria das serifas ou se a instância é estritamente sem serifa (Sans-Serif).",
            "Weight": "PESO:\nAvalia a espessura do traço principal. Mapeado automaticamente via Weight Class da instância.",
            "Proportion": "PROPORÇÃO:\nAnalisa a relação de largura vs. altura. Gerenciado automaticamente via Width Class da instância.",
            "Contrast": "CONTRASTE:\nA diferença proporcional de espessura entre os traço mais finos e os mais grossos da letra.",
            "Stroke Variation": "VARIAÇÃO DO TRAÇO:\nDescreve a transição do traço (se muda gradualmente de forma diagonal, vertical ou se é uniforme).",
            "Arm Style": "ESTILO DOS BRAÇOS:\nAnalisa o formato e a direção das terminações horizontais de letras maiúsculos como 'E', 'F' e 'L'.",
            "Letterform": "FORMA DA LETRA:\nExamina a inclinação. Detecta automaticamente instâncias Itálicas/Oblíquas com base nos eixos Italic/Slant.",
            "Midline": "LINHA MÉDIA:\nDescreve a posição e o tratamento das barras horizontais centrais (como o traço do meio do 'H').",
            "X-Height": "ALTURA-X:\nO tamanho relativo das minúsculas em comparação direta com as maiúsculas desta instância."
        }
        
        self.parameter_name = "openTypeOS2Panose"
        self.keys_order = ["Family Kind", "Serif Style", "Weight", "Proportion", "Contrast", "Stroke Variation", "Arm Style", "Letterform", "Midline", "X-Height"]
        
        self.font = Glyphs.font
        instancias_nomes = [i.name for i in self.font.instances] if self.font else ["Nenhuma fonte aberta"]
        
        self.w = vanilla.FloatingWindow((420, 620), "Configurar PANOSE")
        
        y = 15
        self.w.lbl_instancia = vanilla.TextBox((15, y, 130, 20), "Instância:", sizeStyle="small")
        self.w.pop_instancia = vanilla.PopUpButton((150, y - 2, 255, 20), instancias_nomes, sizeStyle="small", callback=self.ao_mudar_instancia)
        y += 30
        
        self.w.divisoria0 = vanilla.HorizontalLine((15, y, 390, 1))
        y += 12
        
        for key in self.keys_order:
            setattr(self.w, f"lbl_{key.replace(' ', '_')}", vanilla.TextBox((15, y, 130, 20), key, sizeStyle="small"))
            setattr(self.w, f"pop_{key.replace(' ', '_')}", vanilla.PopUpButton((150, y - 2, 255, 20), self.panose_options[key], sizeStyle="small", callback=self.ao_alterar_popup))
            y += 26 # Ajustado de 30 para 26: otimiza o encaixe dos 10 elementos na janela compacta
            
        self.w.divisoria1 = vanilla.HorizontalLine((15, y + 2, 390, 1))
        y += 12
        
        self.w.lbl_preview = vanilla.TextBox((15, y, 390, 20), "Prévia do parâmetro:", sizeStyle="small")
        self.w.txt_preview = vanilla.EditText((15, y + 18, 390, 22), "", sizeStyle="small")
        self.w.txt_preview.enable(False)
        y += 46
        
        self.w.divisoria2 = vanilla.HorizontalLine((15, y, 390, 1))
        y += 10
        
        self.w.lbl_ajuda = vanilla.TextBox((15, y, 390, 20), "O que significa:", sizeStyle="small")
        self.w.txt_ajuda = vanilla.TextEditor((15, y + 18, 390, 60), "", readOnly=True)
        y += 88
        
        self.w.btn_ler = vanilla.Button((15, y, 190, 24), "Ler da Instância", callback=self.ler_panose_da_fonte)
        self.w.btn_aplicar = vanilla.Button((215, y, 190, 24), "Aplicar à Instância", callback=self.aplicar_panose_a_fonte)
        y += 32
        
        self.w.btn_replicar = vanilla.Button((15, y, 390, 26), "Aplicar em todas as instâncias", callback=self.replicar_parametros_fixos)
        
        self.ler_panose_da_fonte(None)
        self.atualizar_interface_e_preview(self.keys_order[0])
        
        self.w.open()

    def obter_instancia_atual(self):
        if not self.font or not self.font.instances:
            return None
        idx = self.w.pop_instancia.get()
        if idx < len(self.font.instances):
            return self.font.instances[idx]
        return None

    def ao_mudar_instancia(self, sender):
        self.ler_panose_da_fonte(None)

    def obter_valores_da_interface(self):
        valores_numericos = []
        for key in self.keys_order:
            componente_pop = getattr(self.w, f"pop_{key.replace(' ', '_')}")
            texto_selecionado = componente_pop.getItems()[componente_pop.get()]
            numero_digito = int(texto_selecionado.split('-')[0])
            valores_numericos.append(numero_digito)
        return valores_numericos

    def ao_alterar_popup(self, sender):
        chave_modificada = self.keys_order[0]
        for key in self.keys_order:
            componente_pop = getattr(self.w, f"pop_{key.replace(' ', '_')}")
            if componente_pop == sender:
                chave_modificada = key
                break
        self.atualizar_interface_e_preview(chave_modificada)

    def atualizar_interface_e_preview(self, chave_ativa):
        lista_valores = self.obter_valores_da_interface()
        formato_amigavel = f"panose = {tuple(lista_valores)};"
        self.w.txt_preview.set(formato_amigavel)
        
        if chave_ativa in self.explicacoes_pt:
            self.w.txt_ajuda.set(self.explicacoes_pt[chave_ativa])

    def ler_panose_da_fonte(self, sender):
        self.font = Glyphs.font
        instancia = self.obter_instancia_atual()
        if not instancia:
            return
            
        param_existente = instancia.customParameters[self.parameter_name]
        
        if param_existente and len(param_existente) == 10:
            for idx, key in enumerate(self.keys_order):
                try:
                    valor_alvo = int(param_existente[idx])
                except:
                    continue
                    
                componente_pop = getattr(self.w, f"pop_{key.replace(' ', '_')}")
                
                for item_idx, item_texto in enumerate(self.panose_options[key]):
                    if item_texto.startswith(f"{valor_alvo}-"):
                        componente_pop.set(item_idx)
                        break
            self.atualizar_interface_e_preview(self.keys_order[0])
        else:
            peso_sugerido = self.converter_weightclass_para_panose(instancia.weightClass)
            prop_sugerida = self.converter_widthclass_para_panose(instancia, instancia.widthClass)
            form_sugerida = self.detectar_letterform_italica(instancia)
            
            getattr(self.w, "pop_Weight").set(self.encontrar_index_opcao("Weight", peso_sugerido))
            getattr(self.w, "pop_Proportion").set(self.encontrar_index_opcao("Proportion", prop_sugerida))
            getattr(self.w, "pop_Letterform").set(self.encontrar_index_opcao("Letterform", form_sugerida))
                    
            self.atualizar_interface_e_preview("Letterform")

    def encontrar_index_opcao(self, chave, valor_num):
        for idx, item in enumerate(self.panose_options[chave]):
            if item.startswith(f"{valor_num}-"):
                return idx
        return 0

    def converter_weightclass_para_panose(self, weight_class):
        try: wc = int(weight_class)
        except: return 5
        if wc <= 100: return 2
        elif wc <= 200: return 3
        elif wc <= 300: return 4
        elif wc <= 400: return 5
        elif wc <= 500: return 6
        elif wc <= 600: return 7
        elif wc <= 700: return 8
        elif wc <= 800: return 9
        elif wc <= 900: return 10
        else: return 11

    def converter_widthclass_para_panose(self, instancia, width_class):
        if instancia.customParameters["isFixedPitch"] or (self.font and self.font.customParameters["isFixedPitch"]):
            return 9
        try: wd = int(width_class)
        except: return 3
        if wd in [1, 2]: return 8
        elif wd in [3, 4]: return 6
        elif wd == 5: return 3
        elif wd in [6, 7]: return 5
        elif wd in [8, 9]: return 7
        return 3

    def detectar_letterform_italica(self, instancia):
        eixos_font = self.font.axes if self.font else []
        is_italica = False
        
        for idx, eixo in enumerate(eixos_font):
            tag_eixo = eixo.axisTag.lower() if hasattr(eixo, "axisTag") else ""
            if "ital" in tag_eixo or "slnt" in tag_eixo:
                if idx < len(instancia.axes) and instancia.axes[idx] > 0:
                    is_italica = True
                    break
                    
        if not is_italica and "italic" in instancia.name.lower():
            is_italica = True
            
        return 9 if is_italica else 2

    def aplicar_panose_a_fonte(self, sender):
        self.font = Glyphs.font
        instancia = self.obter_instancia_atual()
        if not instancia: return
        lista_panose = self.obter_valores_da_interface()
        self.font.disableUpdateInterface()
        try:
            instancia.customParameters[self.parameter_name] = lista_panose
            if self.font.currentTab:
                self.font.currentTab.updateKerning()
            if sender:
                Glyphs.showNotification("Instância Atualizada", f"PANOSE salvo em '{instancia.name}'")
        except Exception as e:
            print(f"❌ Erro: {str(e)}")
        finally:
            self.font.enableUpdateInterface()

    def replicar_parametros_fixos(self, sender):
        self.font = Glyphs.font
        if not self.font or not self.font.instances:
            Glyphs.displayDialog("Abra uma fonte com instâncias")
            return
            
        modelo_atual = self.obter_valores_da_interface()
        self.font.disableUpdateInterface()
        try:
            contador = 0
            for inst in self.font.instances:
                panose_destino = list(modelo_atual)
                
                panose_destino[2] = self.converter_weightclass_para_panose(inst.weightClass)
                panose_destino[3] = self.converter_widthclass_para_panose(inst, inst.widthClass)
                panose_destino[7] = self.detectar_letterform_italica(inst)
                
                inst.customParameters[self.parameter_name] = panose_destino
                contador += 1
                
            Glyphs.clearLog()
            print(f"✅ Automação Tri-Axial concluída com sucesso para {contador} instâncias!")
            Glyphs.showNotification("Replicação Tri-Axial", f"Peso, Proporção e Itálico calculados para {contador} instâncias.")
        except Exception as e:
            print(f"Erro na distribuição automatizada: {str(e)}")
        finally:
            self.font.enableUpdateInterface()

PanoseConfigurator()