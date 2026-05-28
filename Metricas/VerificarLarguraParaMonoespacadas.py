# MenuTitle: Checar Largura de Monoespaçada
# -*- coding: utf-8 -*-

__doc__ = """
Verifica erros em larguras de glifos da master selecionada.
"""

import vanilla

class VerificadorDeLargura:
    def __init__(self):
        # Configurações da Janela ajustadas para o novo conteúdo (Largura, Altura)
        self.w = vanilla.FloatingWindow((260, 135), "Checador de Monoespaçadas")
        
        # Texto descritivo da largura
        self.w.texto_instrucao = vanilla.TextBox((15, 15, 140, 20), "Largura desejada:")
        
        # Caixa de entrada de texto (com valor padrão 540)
        self.w.largura_input = vanilla.EditText((150, 12, 90, 22), "540")
        
        # Nova explicação sobre o relatório detalhado
        self.w.texto_macro = vanilla.TextBox((15, 45, -15, 20), "ℹ️ Detalhes na Macro Window", sizeStyle="small")
        
        # Botão para executar a ação com o novo texto solicitado
        self.w.botao_checar = vanilla.SquareButton((15, 75, -15, 30), "Abrir aba com erros", callback=self.checar_largura)
        
        # Abre a janela na tela
        self.w.open()

    def checar_largura(self, sender):
        # Limpa a Macro Window
        Glyphs.clearLog()
        
        thisFont = Glyphs.font
        if thisFont is None:
            print("Erro: Nenhuma fonte aberta encontrada.")
            return

        # Tenta converter o valor digitado para número inteiro
        try:
            largura_alvo = int(self.w.largura_input.get())
        except ValueError:
            print("Erro: Por favor, insira um número inteiro válido na caixa de largura.")
            Glyphs.showMacroWindow()
            return

        currentMaster = thisFont.selectedFontMaster
        masterID = currentMaster.id

        print(f"Iniciando checagem na fonte: {thisFont.familyName}")
        print(f"Master selecionada: {currentMaster.name}")
        print(f"Buscando glifos com largura DIFERENTE de: {largura_alvo}")
        print("-" * 50)
        
        glifos_invalidos = []

        # Mostra a Macro Window para exibir o relatório
        Glyphs.showMacroWindow()

        # Percorre os glifos
        for glyph in thisFont.glyphs:
            layer = glyph.layers[masterID]
            
            if layer is not None:
                largura_atual = layer.width
                
                if largura_atual != largura_alvo:
                    print(f"⚠️ Glifo: [{glyph.name}] | Largura atual: {largura_atual}")
                    glifos_invalidos.append(glyph.name)

        print("-" * 50)
        
        # Se encontrou erros, abre na Edit View
        if len(glifos_invalidos) > 0:
            print(f"Fim da checagem. Abrindo {len(glifos_invalidos)} glifos em uma nova aba para correção.")
            texto_da_aba = "/" + "/".join(glifos_invalidos)
            thisFont.newTab(texto_da_aba)
        else:
            print(f"✅ Sucesso! Todos os glifos na master '{currentMaster.name}' têm a largura exata de {largura_alvo}.")

# Executa a interface gráfica
VerificadorDeLargura()
