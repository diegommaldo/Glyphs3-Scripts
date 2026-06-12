#MenuTitle: Samba de arredondar métricas
# -*- coding: utf-8 -*-
__doc__ = """
Para os glifos selecionados, move todas as métricas +1 e depois -1 no eixo X
para forçar o arredondamento das entrelinhas e valores de largura.
"""

import GlyphsApp

font = Glyphs.font
glifos_selecionados = [layer.parent for layer in font.selectedLayers]

if not glifos_selecionados:
    print("❌ Nenhum glifo selecionado.")
else:
    for glifo in glifos_selecionados:
        for camada in glifo.layers:
            camada.LSB += 1
            camada.RSB += 1
            camada.LSB -= 1
            camada.RSB -= 1

    print("✅ Samba de Métricas dançado em %d glifo(s)." % len(glifos_selecionados))