#MenuTitle: Paste Components in All Masters
# -*- coding: utf-8 -*-
__doc__="""
This script deletes existing content and pastes components in all masters.
"""

def main():
    font = Glyphs.font
    
    # Garante que há um glifo selecionado
    if not font.selectedLayers:
        print("⚠️ No glyph selected")
        return
        
    selectedLayer = font.selectedLayers[0]
    selectedGlyph = selectedLayer.parent
    selectedComponents = selectedLayer.components
    
    # Desativa a atualização da interface para rodar mais rápido
    font.disableUpdateInterface()
    
    try:
        for master in font.masters:
            # Ignora a master ativa atual (de onde estamos copiando)
            if master != font.selectedFontMaster:
                newLayer = selectedGlyph.layers[master.id]
                
                # Deleta todo o conteúdo existente na camada de destino
                newLayer.clear() 
                
                # Cola os componentes copiados da master ativa
                for component in selectedComponents:
                    newLayer.components.append(component.copy())
                    
        print(f"✅ Components pasted at all masters in: {selectedGlyph.name}")
                    
    except Exception as e:
        print(f"💥 Error processing the script: {e}")
        
    finally:
        # Reativa a interface do software
        font.enableUpdateInterface()

if __name__ == '__main__':
    main()
