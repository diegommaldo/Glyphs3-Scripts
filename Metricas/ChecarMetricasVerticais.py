# MenuTitle: Checar alinhamentos de métricas verticais
# encoding: utf-8

__doc__ = """
Checa se as métricas dos glifos batem 
com o que foi definido nos parâmetros 
em “Info > Masters"
"""

import vanilla

# 0. Limpa a janela do Macro Panel para o relatório
Glyphs.clearLog()

class QCMasterInterface(object):
	def __init__(self):
		# Janela aumentada para 365 para acomodar os novos campos de tolerância
		self.w = vanilla.FloatingWindow((320, 365), "Checar Métricas")
		
		# Texto descritivo
		self.w.instrucao = vanilla.TextBox((20, 15, -20, 40), 
											"Selecione a checagem de possíveis erros nas linhas de referência (resposta na macro):")
		
		# Opções de Linhas de Referência
		self.w.checar_xheight = vanilla.CheckBox((20, 60, -20, 20), "Checar x-Height e Baseline", value=True)
		self.w.checar_ascender = vanilla.CheckBox((20, 85, -20, 20), "Checar Ascender", value=False)
		self.w.checar_capheight = vanilla.CheckBox((20, 110, -20, 20), "Checar Cap Height", value=False)
		self.w.checar_smallcaps = vanilla.CheckBox((20, 135, -20, 20), "Checar Small Caps (ref: h.sc)", value=False)
		
		# --- NOVOS CAMPOS: Tolerância de Erro ---
		self.w.texto_erro_min = vanilla.TextBox((20, 167, 70, 20), "Erro mín:")
		self.w.erro_min_input = vanilla.EditText((90, 165, 45, 22), "1")
		
		self.w.texto_erro_max = vanilla.TextBox((155, 167, 70, 20), "Erro máx:")
		self.w.erro_max_input = vanilla.EditText((225, 165, 45, 22), "3")
		
		# Opções de escopo (Radio Group) - movido para baixo
		self.w.escolha_master = vanilla.RadioGroup((20, 200, -20, 45), 
													["Master selecionada", "Todas as Masters"],
													isVertical=True)
		self.w.escolha_master.set(0)
		
		# --- CHECKBOX NO FINAL DE TUDO ---
		self.w.abrir_aba = vanilla.CheckBox((20, 255, -20, 20), "🔠 Abrir glifos com erro em nova aba", value=False)
		
		# Botão para rodar a checagem
		self.w.botao_rodar = vanilla.Button((20, 295, -20, 30), "Verificar", callback=self.rodar_checagem)
		
		# Abre a janela
		self.w.open()
		
	def descobrir_altura_sc_geometricamente(self, font, master_id):
		"""Descobre o x-height das Small Caps medindo a altura real de um glifo .sc de controle"""
		glifos_controle = ["h.sc", "h.smcp"]
		
		for nome in glifos_controle:
			glyph = font.glyphs[nome]
			if glyph:
				layer = glyph.layers[master_id]
				if layer and len(layer.paths) > 0:
					topo_real = int(round(layer.bounds.origin.y + layer.bounds.size.height))
					if topo_real > 0:
						return topo_real
		return None

	def rodar_checagem(self, sender):
		Glyphs.showMacroWindow()
		Glyphs.clearLog()
		
		font = Glyphs.font
		if not font:
			print("Erro: Nenhum documento aberto.")
			return
			
		run_xheight = self.w.checar_xheight.get()
		run_ascender = self.w.checar_ascender.get()
		run_capheight = self.w.checar_capheight.get()
		run_smallcaps = self.w.checar_smallcaps.get()
		abrir_em_aba = self.w.abrir_aba.get()
		
		if not any([run_xheight, run_ascender, run_capheight, run_smallcaps]):
			print("Aviso: Selecione pelo menos uma linha de referência para verificar.")
			return
			
		# Captura e valida os valores de erro mínimo e máximo inseridos pelo usuário
		try:
			erro_min = int(self.w.erro_min_input.get())
			erro_max = int(self.w.erro_max_input.get())
		except ValueError:
			print("Erro: Insira apenas números inteiros válidos nos campos de Erro Mín/Máx.")
			return
			
		if erro_min > erro_max:
			print("Aviso: O erro mínimo não pode ser maior que o erro máximo.")
			return
			
		baseline = 0
		
		if self.w.escolha_master.get() == 0:
			masters_para_checar = [font.selectedFontMaster]
			print(f"–––> Buscando na master ativa (Tolerância: {erro_min} a {erro_max} un) <––––")
		else:
			masters_para_checar = font.masters
			print(f"–––> Buscando em todas as masters (Tolerância: {erro_min} a {erro_max} un) <––––")
			
		if font.selectedLayers and len(font.selectedLayers) > 0:
			glifos_para_varrer = [layer.parent for layer in font.selectedLayers if layer.parent and layer.parent.category == "Letter"]
			print(f"Escopo: Analisando apenas os {len(glifos_para_varrer)} glifos selecionados.")
		else:
			glifos_para_varrer = [glyph for glyph in font.glyphs if glyph.category == "Letter"]
			print(f"Escopo: Nenhum glifo selecionado. Analisando todos os {len(glifos_para_varrer)} glifos da fonte.")
			
		total_glifos_sinalizados = 0
		camadas_para_abrir = []
		
		for master in masters_para_checar:
			x_height = int(master.xHeight)
			ascender = int(master.ascender)
			cap_height = int(master.capHeight)
			
			sc_height = self.descobrir_altura_sc_geometricamente(font, master.id)
			
			sc_valido = run_smallcaps and sc_height is not None
			if run_smallcaps and sc_height is None:
				print(f"\nAviso: Não foi possível determinar a altura das Small Caps automaticamente. Crie um glifo 'a.sc' ou 'x.sc' com caminhos para servir de referência na Master '{master.name}'.")
			
			sc_info_str = f" | Small Caps → {sc_height}" if sc_valido else ""
			print(f"\n{master.name} (x-Height → {x_height} | Cap Height → {cap_height} | Ascender → {ascender}{sc_info_str})")
			print("-" * 40)
			
			glifos_na_master = 0
			
			for glyph in glifos_para_varrer:
				layer = glyph.layers[master.id]
				linhas_com_erro = set()
				
				is_smallcap_glyph = ".sc" in glyph.name or ".smcp" in glyph.name
				is_uppercase = (glyph.subCategory == "Uppercase") or (glyph.name.isupper() and len(glyph.name) == 1)
				
				for path in layer.paths:
					for node in path.nodes:
						node_y = int(round(node.y))
						
						# 1. ESCOPO: GLIFOS SMALL CAPS
						if is_smallcap_glyph:
							if sc_valido:
								dist_sc = abs(node_y - sc_height)
								if erro_min <= dist_sc <= erro_max:
									linhas_com_erro.add("Small Caps")
							
							dist_baseline = abs(node_y - baseline)
							if (run_xheight or run_smallcaps) and (erro_min <= dist_baseline <= erro_max):
								linhas_com_erro.add("Baseline")
								
						# 2. ESCOPO: GLIFOS MAIÚSCULOS (Uppercase)
						elif is_uppercase:
							if run_capheight:
								dist_cap = abs(node_y - cap_height)
								if erro_min <= dist_cap <= erro_max:
									linhas_com_erro.add("Cap Height")
							
							dist_baseline = abs(node_y - baseline)
							if (run_xheight or run_capheight) and (erro_min <= dist_baseline <= erro_max):
								linhas_com_erro.add("Baseline")
								
						# 3. ESCOPO: MINÚSCULAS COMUNS
						else:
							if run_xheight:
								dist_xHeight = abs(node_y - x_height)
								dist_baseline = abs(node_y - baseline)
								
								if erro_min <= dist_xHeight <= erro_max:
									linhas_com_erro.add("x-Height")
								if erro_min <= dist_baseline <= erro_max:
									linhas_com_erro.add("Baseline")
							
							if run_ascender:
								dist_ascender = abs(node_y - ascender)
								if erro_min <= dist_ascender <= erro_max:
									linhas_com_erro.add("Ascender")
								
				if linhas_com_erro:
					locais_formatados = ", ".join(sorted(linhas_com_erro))
					print(f"⚠️ Desalinhamento em: {glyph.name} ({locais_formatados})")
					glifos_na_master += 1
					total_glifos_sinalizados += 1
					
					camadas_para_abrir.append(layer)
						
			if glifos_na_master == 0:
				print("✅ Nenhum erro encontrado nesta Master.")
			else:
				print(" ")
				print(f"Problemas na Master → {glifos_na_master}")
				
		print("\n========================================")
		print(f"Total de erros → {total_glifos_sinalizados}")
		
		if abrir_em_aba and len(camadas_para_abrir) > 0:
			nova_aba = font.newTab()
			nova_aba.layers = camadas_para_abrir
			print(f"\n📂 Nova aba criada com os {len(camadas_para_abrir)} glifos exibidos em suas respectivas masters de erro.")

# Inicializa a interface
QCMasterInterface()
