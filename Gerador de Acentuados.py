# MenuTitle: Gerador de Glifos Acentuados
# encoding: utf-8

import vanilla
import GlyphsApp

# 0. Limpa a janela do Macro Panel para o relatório
Glyphs.clearLog()

class GeradorAcentosInterface(object):
    def __init__(self):
        # Janela (370x620)
        self.w = vanilla.FloatingWindow((370, 640), "Gerador de Acentuados")
        
        # --- OPÇÕES DE ESCOPO DE ANÁLISE (PRIMEIRO) ---
        self.w.texto_escopo = vanilla.TextBox((20, 10, -20, 20), "Letras base a partir de:")
        self.w.escolha_escopo = vanilla.RadioGroup((20, 32, -20, 45), 
                                                    ["Apenas glifos selecionados", "Todos os glifos na fonte"],
                                                    isVertical=True)
        self.w.escolha_escopo.set(0)
        
        self.w.linha_div_escopo = vanilla.HorizontalLine((20, 85, -20, 1))
        
        # --- SELEÇÃO EM LOTE POR REGIÕES / CHARACTER SETS ---
        self.w.texto_regioes = vanilla.TextBox((20, 95, -20, 20), "Ativar por Região / Conjunto:")
        
        # Colona 1 de Regiões
        self.w.regiao_portugues = vanilla.CheckBox((20, 117, 140, 20), "Português", value=True, callback=self.evento_regiao_checkbox)
        self.w.regiao_western = vanilla.CheckBox((20, 139, 140, 20), "Western Euro", value=False, callback=self.evento_regiao_checkbox)
        self.w.regiao_central = vanilla.CheckBox((20, 161, 140, 20), "Central Euro", value=False, callback=self.evento_regiao_checkbox)
        
        # Coluna 2 de Regiões
        self.w.regiao_se_euro = vanilla.CheckBox((170, 117, 150, 20), "SE European", value=False, callback=self.evento_regiao_checkbox)
        self.w.regiao_vietnam = vanilla.CheckBox((170, 139, 150, 20), "Vietnamese", value=False, callback=self.evento_regiao_checkbox)
        self.w.regiao_todos = vanilla.CheckBox((170, 161, 150, 20), "Todos Possíveis", value=False, callback=self.evento_regiao_checkbox)
        
        self.w.linha_div_regiao = vanilla.HorizontalLine((20, 187, -20, 1))
        
        # --- CHECKBOXES INDIVIDUAIS DOS DIACRÍTICOS ---
        self.w.instrucao = vanilla.TextBox((20, 195, 160, 20), "Acentos ativos")
        
        # Botões Marcar/Desmarcar Todos
        self.w.botao_desmarcar = vanilla.Button((180, 192, 80, 22), "Nenhum", callback=self.desmarcar_todos_diacriticos)
        self.w.botao_marcar = vanilla.Button((265, 192, 80, 22), "Todos", callback=self.marcar_todos_diacriticos)
        
        # Dicionário para armazenar checkboxes de diacríticos (otimização)
        self.diacriticos_checkboxes = {}
        
        # Checkboxes para os Diacríticos (Coluna 1)
        self.diacriticos_checkboxes["acute"] = vanilla.CheckBox((20, 240, 140, 20), "Agudo", value=True)
        self.diacriticos_checkboxes["grave"] = vanilla.CheckBox((20, 262, 140, 20), "Crase", value=True)
        self.diacriticos_checkboxes["dieresis"] = vanilla.CheckBox((20, 284, 140, 20), "Trema", value=False)
        self.diacriticos_checkboxes["circumflex"] = vanilla.CheckBox((20, 306, 140, 20), "Circunflexo", value=True)
        self.diacriticos_checkboxes["tilde"] = vanilla.CheckBox((20, 328, 140, 20), "Til", value=True)
        self.diacriticos_checkboxes["hookabove"] = vanilla.CheckBox((20, 350, 140, 20), "Gancho (hookabove)", value=False)
        self.diacriticos_checkboxes["horn"] = vanilla.CheckBox((20, 372, 140, 20), "Chifre (horn)", value=False)
        
        # Checkboxes para os Diacríticos (Coluna 2)
        self.diacriticos_checkboxes["cedilla"] = vanilla.CheckBox((170, 240, 140, 20), "Cedilha", value=True)
        self.diacriticos_checkboxes["macron"] = vanilla.CheckBox((170, 262, 140, 20), "Macron", value=False)
        self.diacriticos_checkboxes["macronbelow"] = vanilla.CheckBox((170, 284, 140, 20), "Macron Inf.", value=False)
        self.diacriticos_checkboxes["breve"] = vanilla.CheckBox((170, 306, 140, 20), "Breve", value=False)
        self.diacriticos_checkboxes["ring"] = vanilla.CheckBox((170, 328, 140, 20), "Anel", value=False)
        self.diacriticos_checkboxes["caron"] = vanilla.CheckBox((170, 350, 140, 20), "Caron", value=False)
        self.diacriticos_checkboxes["dotbelow"] = vanilla.CheckBox((170, 372, 140, 20), "Ponto Inf. (dotbelow)", value=False)
        self.diacriticos_checkboxes["ogonek"] = vanilla.CheckBox((170, 394, 140, 20), "Ogonek", value=False)
        
        # Atributos de atalho para compatibilidade (mantém referências diretas)
        self.w.acute = self.diacriticos_checkboxes["acute"]
        self.w.grave = self.diacriticos_checkboxes["grave"]
        self.w.dieresis = self.diacriticos_checkboxes["dieresis"]
        self.w.circumflex = self.diacriticos_checkboxes["circumflex"]
        self.w.tilde = self.diacriticos_checkboxes["tilde"]
        self.w.hookabove = self.diacriticos_checkboxes["hookabove"]
        self.w.horn = self.diacriticos_checkboxes["horn"]
        self.w.cedilla = self.diacriticos_checkboxes["cedilla"]
        self.w.macron = self.diacriticos_checkboxes["macron"]
        self.w.macronbelow = self.diacriticos_checkboxes["macronbelow"]
        self.w.breve = self.diacriticos_checkboxes["breve"]
        self.w.ring = self.diacriticos_checkboxes["ring"]
        self.w.caron = self.diacriticos_checkboxes["caron"]
        self.w.dotbelow = self.diacriticos_checkboxes["dotbelow"]
        self.w.ogonek = self.diacriticos_checkboxes["ogonek"]
        
        # Lista de diacríticos para iteração
        self.lista_diacriticos = list(self.diacriticos_checkboxes.keys())
        
        # --- FILTRO POR CAIXA DO GLIFO ---
        self.w.linha_div_caixa = vanilla.HorizontalLine((20, 422, -20, 1))
        self.w.texto_caixa = vanilla.TextBox((20, 430, -20, 20), "Caixas:")
        self.w.gerar_uppercase = vanilla.CheckBox((20, 452, 140, 20), "Maiúsculas", value=True)
        self.w.gerar_lowercase = vanilla.CheckBox((170, 452, 140, 20), "Minúsculas", value=True)
        self.w.gerar_smallcaps = vanilla.CheckBox((20, 474, -20, 20), "Small Caps (.sc / .smcp)", value=False)
        
        # Linha divisória abaixo de Small Caps
        self.w.linha_div_smallcaps = vanilla.HorizontalLine((20, 500, -20, 1))
        
        # Checkboxes de controle no final
        self.w.incluir_alternativos = vanilla.CheckBox((20, 510, 140, 20), "Incluir alts. (.ss01...)", value=False)
        self.w.gerar_duplos = vanilla.CheckBox((170, 510, 160, 20), "Acentos duplos (vietnamita)", value=False)
        
        # --- CHECKBOX: Forçar Regerar ---
        self.w.regerar_existentes = vanilla.CheckBox((20, 538, -20, 20), "Substituir glifos existentes", value=False)
        self.w.abrir_aba = vanilla.CheckBox((20, 560, -20, 20), "🔠 Abrir glifos em nova aba", value=True)
        
        # Botão para executar o processo
        self.w.botao_rodar = vanilla.Button((20, 595, -20, 30), "Gerar glifos acentuados", callback=self.gerar_acentos)
        
        # Dicionário estrito de mapeamento de caracteres por diacrítico e região
        self.mapa_legal = {
            "portugues": {
                "acute": ["a", "e", "i", "o", "u"],
                "grave": ["a"],
                "circumflex": ["a", "e", "o"],
                "tilde": ["a", "o"],
                "cedilla": ["c"]
            },
            "western": {
                "acute": ["a", "e", "i", "o", "u", "y"],
                "grave": ["a", "e", "i", "o", "u"],
                "dieresis": ["a", "e", "i", "o", "u", "y"],
                "circumflex": ["a", "e", "i", "o", "u"],
                "tilde": ["a", "n", "o"],
                "cedilla": ["c"],
                "ring": ["a"]
            },
            "central": {
                "acute": ["a", "c", "e", "i", "l", "n", "o", "r", "s", "u", "y", "z"],
                "dieresis": ["a", "e", "i", "o", "u", "y"],
                "circumflex": ["a", "e", "i", "o", "u"],
                "cedilla": ["c", "s", "t"],
                "macron": ["a", "e", "i", "o", "u"],
                "macronbelow": ["a", "e", "i", "o", "u"],
                "breve": ["a", "e", "g", "u"],
                "ring": ["a", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"],
                "ogonek": ["a", "e", "i", "u"]
            },
            "se_euro": {
                "acute": ["a", "e", "i", "o", "u", "g", "k", "l", "n", "r", "s", "z"],
                "grave": ["a", "e", "i", "o", "u"],
                "dieresis": ["a", "e", "i", "o", "u"],
                "circumflex": ["a", "e", "i", "o", "u", "c", "g", "h", "j", "s", "w", "y"],
                "cedilla": ["c", "g", "k", "l", "n", "r", "s", "t"],
                "breve": ["a", "e", "g", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"]
            },
            "vietnam": {
                "acute": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex"],
                "grave": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex"],
                "circumflex": ["a", "e", "o"],
                "tilde": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex"],
                "hookabove": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex"],
                "horn": ["o", "u"],
                "breve": ["a"],
                "dotbelow": ["a", "e", "i", "o", "u", "y", "ohorn", "uhorn", "abreve", "acircumflex", "ecircumflex", "ocircumflex"]
            },
            "todos": {
                "acute": ["a", "e", "i", "o", "u", "y", "c", "g", "k", "l", "n", "r", "s", "z"],
                "grave": ["a", "e", "i", "o", "u"],
                "dieresis": ["a", "e", "i", "o", "u", "y"],
                "circumflex": ["a", "e", "i", "o", "u", "c", "g", "h", "j", "s", "w", "y"],
                "tilde": ["a", "e", "i", "o", "u", "y", "n"],
                "hookabove": ["a", "e", "i", "o", "u", "y"],
                "horn": ["o", "u"],
                "cedilla": ["c", "g", "k", "l", "n", "r", "s", "t"],
                "macron": ["a", "e", "i", "o", "u"],
                "macronbelow": ["a", "e", "i", "o", "u"],
                "breve": ["a", "e", "g", "u"],
                "ring": ["a", "u"],
                "caron": ["c", "d", "e", "l", "n", "r", "s", "t", "z"],
                "dotbelow": ["a", "e", "i", "o", "u", "y"],
                "ogonek": ["a", "e", "i", "u"]
            }
        }
        
        # Cache de glifos combinantes para validação (otimização)
        self.cache_combinantes = {}
        
        # Inicializa chamando o callback para o estado default (Português ativo)
        self.evento_regiao_checkbox(None)
        self.w.open()

    def desmarcar_todos_diacriticos(self, sender):
        """Desativa todos os checkboxes de diacríticos individuais"""
        for checkbox in self.diacriticos_checkboxes.values():
            checkbox.set(False)

    def marcar_todos_diacriticos(self, sender):
        """Ativa todos os checkboxes de diacríticos individuais"""
        for checkbox in self.diacriticos_checkboxes.values():
            checkbox.set(True)

    def evento_regiao_checkbox(self, sender):
        """Gerencia a ativação visual acumulada dos diacríticos conforme as regiões marcadas"""
        definicao_regioes = {
            "portugues": ["acute", "grave", "circumflex", "tilde", "cedilla"],
            "western": ["acute", "grave", "dieresis", "circumflex", "tilde", "cedilla", "ring"],
            "central": ["acute", "dieresis", "circumflex", "cedilla", "macron", "macronbelow", "breve", "ring", "caron", "ogonek"],
            "se_euro": ["acute", "grave", "dieresis", "circumflex", "cedilla", "breve", "caron"],
            "vietnam": ["acute", "grave", "circumflex", "tilde", "hookabove", "horn", "breve", "dotbelow"],
            "todos": ["acute", "grave", "dieresis", "circumflex", "tilde", "hookabove", "horn", "cedilla", "macron", "macronbelow", "breve", "ring", "caron", "dotbelow", "ogonek"]
        }
        
        diacriticos_para_ativar = set()
        
        if self.w.regiao_portugues.get(): diacriticos_para_ativar.update(definicao_regioes["portugues"])
        if self.w.regiao_western.get(): diacriticos_para_ativar.update(definicao_regioes["western"])
        if self.w.regiao_central.get(): diacriticos_para_ativar.update(definicao_regioes["central"])
        if self.w.regiao_se_euro.get(): diacriticos_para_ativar.update(definicao_regioes["se_euro"])
        if self.w.regiao_vietnam.get(): diacriticos_para_ativar.update(definicao_regioes["vietnam"])
        if self.w.regiao_todos.get(): diacriticos_para_ativar.update(definicao_regioes["todos"])
        
        if not diacriticos_para_ativar:
            return
        
        # Atualiza todos os checkboxes de uma vez
        for diacritico, checkbox in self.diacriticos_checkboxes.items():
            checkbox.set(diacritico in diacriticos_para_ativar)
        
        if self.w.regiao_vietnam.get() or self.w.regiao_todos.get():
            self.w.gerar_duplos.set(True)
        else:
            self.w.gerar_duplos.set(False)

    def verificar_combinante(self, font, nome_combinante):
        """Verifica se um glifo combinante existe na fonte (com cache)"""
        if nome_combinante in self.cache_combinantes:
            return self.cache_combinantes[nome_combinante]
        
        existe = nome_combinante in font.glyphs
        self.cache_combinantes[nome_combinante] = existe
        return existe

    def gerar_acentos(self, sender):
        Glyphs.showMacroWindow()
        Glyphs.clearLog()
        
        font = Glyphs.font
        if not font:
            print("Erro: Nenhum documento aberto.")
            return
        
        # Limpa o cache de combinantes para esta execução
        self.cache_combinantes = {}
        
        # Coleta diacríticos ativos usando o dicionário (otimizado)
        diacriticos_alvo = [d for d in self.lista_diacriticos if self.diacriticos_checkboxes[d].get()]
        
        if not diacriticos_alvo:
            print("Aviso: Selecione pelo menos um diacrítico para gerar.")
            return
            
        caixa_upper = self.w.gerar_uppercase.get()
        caixa_lower = self.w.gerar_lowercase.get()
        caixa_sc = self.w.gerar_smallcaps.get()
        
        if not any([caixa_upper, caixa_lower, caixa_sc]):
            print("Aviso: Selecione pelo menos um tipo de caixa.")
            return
            
        permitir_sufixos = self.w.incluir_alternativos.get()
        permitir_duplos = self.w.gerar_duplos.get()
        deve_regerar = self.w.regerar_existentes.get()
            
        if self.w.escolha_escopo.get() == 0:
            if not font.selectedLayers:
                print("Aviso: Nenhum glifo selecionado no Font View.")
                return
            brutos = [layer.parent for layer in font.selectedLayers if layer.parent and layer.parent.category == "Letter"]
        else:
            brutos = [glyph for glyph in font.glyphs if glyph.category == "Letter"]
            
        # Separa os glifos por tipo
        letras_base = []
        for g in brutos:
            # Verifica se é um glifo de small cap
            nome = g.name
            if ".sc" in nome or ".smcp" in nome:
                # É um small cap, processa separadamente
                if caixa_sc:
                    letras_base.append(g)
            else:
                # Glifo normal
                letras_base.append(g)

        print(f"–––> Analisando base de dados: {len(letras_base)} glifos candidatos encontrados <––––")
        
        glifos_criados = []
        font.disableUpdateInterface()
        
        caracteres_estreitos = set(["i", "j", "l", "t", "f", "r", "i.sc", "j.sc", "l.sc", "t.sc"])
        diacriticos_sem_narrow = set(["ogonek", "cedilla", "dotbelow", "macronbelow"])
        
        # Pré-calcula regiões ativas para otimização
        regioes_ativas = []
        if self.w.regiao_portugues.get(): regioes_ativas.append("portugues")
        if self.w.regiao_western.get(): regioes_ativas.append("western")
        if self.w.regiao_central.get(): regioes_ativas.append("central")
        if self.w.regiao_se_euro.get(): regioes_ativas.append("se_euro")
        if self.w.regiao_vietnam.get(): regioes_ativas.append("vietnam")
        usar_todas_regioes = self.w.regiao_todos.get()
        
        try:
            for base_glyph in letras_base:
                raw_name = base_glyph.name
                
                if "." in raw_name:
                    partes = raw_name.split(".", 1)
                    base_clean = partes[0]
                    sufixo = "." + partes[1]
                else:
                    base_clean = raw_name
                    sufixo = ""
                
                # Determina o tipo de caixa
                eh_maiuscula = (base_glyph.subCategory == "Uppercase") or (base_glyph.case == 1)
                eh_smallcap = (".sc" in raw_name or ".smcp" in raw_name) or (base_glyph.case == 3)
                eh_minuscula = not eh_maiuscula and not eh_smallcap
                
                # Filtra por caixa
                if eh_maiuscula and not caixa_upper: continue
                if eh_minuscula and not caixa_lower: continue
                if eh_smallcap and not caixa_sc: continue
                
                # Para small caps, a raiz é sempre minúscula
                if eh_smallcap:
                    raiz_em_caixa_baixa = base_clean.lower()
                else:
                    raiz_em_caixa_baixa = base_clean.lower()
                
                precisa_narrow = (raiz_em_caixa_baixa in caracteres_estreitos) or (raw_name.lower() in caracteres_estreitos)
                
                for acc in diacriticos_alvo:
                    # --- VALIDAÇÃO DE IDIOMA E COMPATIBILIDADE ---
                    if not usar_todas_regioes:
                        valido_na_regiao = False
                        for regiao in regioes_ativas:
                            if acc in self.mapa_legal[regiao] and raiz_em_caixa_baixa in self.mapa_legal[regiao][acc]:
                                valido_na_regiao = True
                                break
                        
                        if not valido_na_regiao:
                            continue
                    
                    # Para small caps, sempre usar a versão minúscula como base
                    if eh_smallcap:
                        base_para_nome = base_clean.lower()
                    else:
                        base_para_nome = base_clean
                    
                    nome_composto_limpo = f"{base_para_nome}{acc}"
                    nome_potencial_final = f"{nome_composto_limpo}{sufixo}"
                    
                    if acc in base_clean.lower() and not permitir_duplos:
                        continue
                    
                    informacao_glifo = Glyphs.glyphInfoForName(nome_composto_limpo)
                    
                    if informacao_glifo and informacao_glifo.category == "Letter":
                        glifo_ja_existe = nome_potencial_final in font.glyphs
                        
                        if glifo_ja_existe and not deve_regerar:
                            continue
                            
                        if not glifo_ja_existe:
                            novo_glifo = GSGlyph(nome_potencial_final)
                            font.glyphs.append(novo_glifo)
                        else:
                            novo_glifo = font.glyphs[nome_potencial_final]
                            
                        # Atualiza informações do glifo
                        if sufixo:
                            novo_glifo.updateGlyphInfo()
                            novo_glifo.category = "Letter"
                            if eh_smallcap:
                                novo_glifo.subCategory = "Lowercase"
                                novo_glifo.case = 3  # Small caps
                            else:
                                novo_glifo.subCategory = informacao_glifo.subCategory
                        else:
                            novo_glifo.updateGlyphInfo()
                            
                        # CRUCIAL: Força a atualização das informações do glifo
                        # Isso garante que a ordenação e categorização estejam corretas
                        novo_glifo.updateGlyphInfo()
                            
                        for master in font.masters:
                            layer = novo_glifo.layers[master.id]
                            
                            layer.clear()
                            layer.anchors = []
                            
                            # Para small caps, usar a versão small cap como base
                            if eh_smallcap:
                                # Tenta encontrar a versão small cap da letra base
                                base_sc = f"{base_clean.lower()}.sc"
                                if base_sc in font.glyphs:
                                    comp_base = GSComponent(base_sc)
                                else:
                                    # Fallback: usa a letra minúscula
                                    comp_base = GSComponent(base_clean.lower())
                            else:
                                comp_base = GSComponent(raw_name)
                            
                            comp_base.alignment = 0
                            layer.components.append(comp_base)
                            
                            nome_acento_final = None
                            
                            # Determina qual diacrítico usar
                            if eh_smallcap:
                                # Para small caps: tenta .sc, .case, ou normal
                                nome_sc = f"{acc}comb.sc"
                                if self.verificar_combinante(font, nome_sc):
                                    nome_acento_final = nome_sc
                                else:
                                    nome_case = f"{acc}comb.case"
                                    if self.verificar_combinante(font, nome_case):
                                        nome_acento_final = nome_case
                                    else:
                                        nome_comb = f"{acc}comb"
                                        if self.verificar_combinante(font, nome_comb):
                                            nome_acento_final = nome_comb
                            elif eh_maiuscula:
                                if precisa_narrow and acc not in diacriticos_sem_narrow:
                                    nome_narrow_case = f"{acc}comb.narrow.case"
                                    if self.verificar_combinante(font, nome_narrow_case):
                                        nome_acento_final = nome_narrow_case
                                
                                if not nome_acento_final:
                                    nome_case_padrao = f"{acc}comb.case"
                                    if self.verificar_combinante(font, nome_case_padrao):
                                        nome_acento_final = nome_case_padrao
                            else:  # Minúsculas
                                if precisa_narrow and acc not in diacriticos_sem_narrow:
                                    nome_narrow_padrao = f"{acc}comb.narrow"
                                    if self.verificar_combinante(font, nome_narrow_padrao):
                                        nome_acento_final = nome_narrow_padrao
                            
                            # Se ainda não encontrou, tenta o padrão
                            if not nome_acento_final:
                                nome_comb_padrao = f"{acc}comb"
                                
                                if sufixo:
                                    nome_com_sufixo = f"{nome_comb_padrao}{sufixo}"
                                    if self.verificar_combinante(font, nome_com_sufixo):
                                        nome_acento_final = nome_com_sufixo
                                
                                if not nome_acento_final and self.verificar_combinante(font, nome_comb_padrao):
                                    nome_acento_final = nome_comb_padrao
                                
                                if not nome_acento_final and self.verificar_combinante(font, acc):
                                    nome_acento_final = acc
                            
                            if nome_acento_final:
                                comp_accent = GSComponent(nome_acento_final)
                                comp_accent.alignment = 0
                                layer.components.append(comp_accent)
                            else:
                                print(f"⚠️ Aviso: Glifo combinante não encontrado para {acc} em {nome_potencial_final}")
                                
                            layer.alignComponents()
                            layer.syncMetrics()
                            
                        # Atualiza novamente após criar as layers
                        novo_glifo.updateGlyphInfo()
                            
                        tipo_status = "Regerado" if glifo_ja_existe else "Gerado"
                        print(f"✅ {tipo_status} com sucesso: {nome_potencial_final} (Acento: {nome_acento_final})")
                        glifos_criados.append(nome_potencial_final)
                        
            # Após processar todos os glifos, forçar atualização geral
            for glyph in glifos_criados:
                if glyph in font.glyphs:
                    font.glyphs[glyph].updateGlyphInfo()
                            
        except Exception as e:
            print(f"Erro durante o processamento: {e}")
            import traceback
            traceback.print_exc()
            
        finally:
            font.enableUpdateInterface()
            if font.currentTab and hasattr(font.currentTab, "graphicView"):
                font.currentTab.graphicView().setNeedsDisplay_(True)
            
        print("\n========================================")
        print(f"Processo concluído. Total de novos glifos processados: {len(glifos_criados)}")
        
        if self.w.abrir_aba.get() and glifos_criados:
            texto_aba = "/" + "/".join(glifos_criados)
            font.newTab(texto_aba)

# Inicializa a interface Vanilla
GeradorAcentosInterface()