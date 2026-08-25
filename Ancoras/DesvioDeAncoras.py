# MenuTitle: Checar desvio de Âncoras
# -*- coding: utf-8 -*-

__doc__="""
Verifica posição das Âncoras
em glifos selecionados
"""

import vanilla

class VerificadorDeAncorasWindow(object):
    def __init__(self):
        # Configura as dimensões da janela UI
        self.w = vanilla.FloatingWindow((320, 220), "Verificador de Âncoras")
        
        # Campo para Tolerância
        self.w.toleranciaTexto = vanilla.TextBox((15, 15, 140, 20), "Tolerância (unidades):")
        self.w.toleranciaInput = vanilla.EditText((160, 12, 60, 22), "15.0")
        
        # Checkboxes para as âncoras padrão
        self.w.checarTop = vanilla.CheckBox((15, 45, 100, 20), "top", value=True)
        self.w.checarBottom = vanilla.CheckBox((15, 70, 120, 20), "bottom", value=True)
        
        # Campo para Âncora Customizada
        self.w.customTexto = vanilla.TextBox((15, 105, 140, 20), "Âncora customizada:")
        self.w.customInput = vanilla.EditText((160, 102, 140, 22), "", placeholder="ex: ogonek, exit")
        
        # Botão para Executar
        self.w.botaoExecutar = vanilla.Button((15, 155, -15, 30), "Verificar Selecionados", callback=self.executar_checagem)
        
        # Abre a janela na tela
        self.w.open()
        
    def executar_checagem(self, sender):
        # Valida a entrada da tolerância
        try:
            tolerancia = float(self.w.toleranciaInput.get())
        except ValueError:
            print("❌ Erro: O valor de tolerância precisa ser um número válido.")
            return
            
        # Monta a lista de âncoras com base nas escolhas da interface
        ancoras_para_checar = []
        if self.w.checarTop.get():
            ancoras_para_checar.append("top")
        if self.w.checarBottom.get():
            ancoras_para_checar.append("bottom")
            
        # Adiciona a âncora customizada se o campo não estiver vazio
        ancora_customizada = self.w.customInput.get().strip()
        if ancora_customizada:
            ancoras_para_checar.append(ancora_customizada)
            
        # Se nenhuma âncora foi selecionada ou digitada, interrompe
        if not ancoras_para_checar:
            print("⚠️ Nenhuma âncora foi selecionada para verificação.")
            return
            
        font = Glyphs.font
        if not font or not font.selectedLayers:
            print("⚠️ Nenhum glifo selecionado na fonte.")
            return
            
        # Inicia o processo de checagem
        font.disableUpdateInterface()
        print("🔍 INICIANDO CHECAGEM DE ÂNCORAS")
        print("-> Alvos: {}".format(", ".join(["'{}'".format(a) for a in ancoras_para_checar])))
        print("-> Tolerância: {} unidades\n".format(tolerancia))
        
        alinhadas = 0
        desalinhadas = 0
        
        for layer in font.selectedLayers:
            glyph = layer.parent
            glyph_name = glyph.name
            
            for current_layer in glyph.layers:
                # Foca apenas em Master Layers ou Camadas Especiais (Brackets/Responsores)
                if not current_layer.isMasterLayer and not current_layer.isSpecialLayer:
                    continue
                    
                master_name = current_layer.master.name
                centro_horizontal = current_layer.width / 2.0
                
                for nome_ancora in ancoras_para_checar:
                    ancora = current_layer.anchors[nome_ancora]
                    
                    if ancora:
                        posicao_x = ancora.position.x
                        desvio = abs(posicao_x - centro_horizontal)
                        
                        if desvio > tolerancia:
                            desalinhadas += 1
                            print("❌ Glifo: {} | Master: '{}'".format(glyph_name, master_name))
                            print("   -> Âncora '{}' está desalinhada!".format(nome_ancora))
                            print("   -> X da Âncora: {} | Centro Ideal: {}".format(posicao_x, centro_horizontal))
                            print("   -> Desvio: {} unidades\n".format(round(desvio, 2)))
                        else:
                            alinhadas += 1
                            
        font.enableUpdateInterface()
        print("✅ Checagem concluída!")
        print("-> Encontradas: {} alinhadas | {} fora da tolerância.\n".format(alinhadas, desalinhadas))

# Inicializa a interface
VerificadorDeAncorasWindow()