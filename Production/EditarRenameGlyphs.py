# MenuTitle: Editar Rename Glyphs
# -*- coding: utf-8 -*-
__doc__="""
Edita o Rename Glyphs em uma ou 
mais instâncias ao mesmo tempo
"""

import vanilla
from GlyphsApp import Glyphs, GSInstance

class RenameGlyphsBatchEditor(object):
	def __init__(self):
		self.font = Glyphs.font
		if not self.font:
			Glyphs.showNotification("Nenhuma fonte aberta", "Por favor, abra um arquivo de fonte primeiro.")
			return

		# Identificar os índices dos eixos de Weight e Width no Glyphs 3
		self.weight_axis_index = None
		self.width_axis_index = None
		
		if self.font.axes:
			for i, axis in enumerate(self.font.axes):
				tag = getattr(axis, "axisTag", None) or getattr(axis, "tag", "")
				if tag == "wght" or axis.name.lower() == "weight":
					self.weight_axis_index = i
				elif tag == "wdth" or axis.name.lower() == "width":
					self.width_axis_index = i

		# Listas de classes baseadas nos eixos das INSTÂNCIAS (Exports)
		self.weights = set()
		self.widths = set()

		# Extrair os valores dos eixos de forma segura
		for inst in self.font.instances:
			if hasattr(inst, "axes") and inst.axes is not None:
				weight_val = self.obter_valor_eixo(inst, self.weight_axis_index, fallback_index=0)
				width_val = self.obter_valor_eixo(inst, self.width_axis_index, fallback_index=1)
				
				self.weights.add(str(weight_val))
				self.widths.add(str(width_val))

		# Ordenar numericamente
		self.weights = sorted(list(self.weights), key=lambda x: int(x) if x.isdigit() else 0)
		self.widths = sorted(list(self.widths), key=lambda x: int(x) if x.isdigit() else 0)

		# Configurações de tamanho da janela
		window_width = 500
		window_height = 600
		self.w = vanilla.FloatingWindow(
			(window_width, window_height), 
			"Editar Rename Glyphs", 
			minSize=(450, 500)
		)

		# --- SEÇÃO DE FILTROS ---
		# Box contendo as listas de seleção múltipla lado a lado
		self.w.boxFiltro = vanilla.Box((10, 10, -10, 160))
		self.w.boxFiltro.titulo = vanilla.TextBox((10, 5, -10, 20), "Filtrar Instâncias (Selecione uma ou mais)", sizeStyle="small")
		
		# Lista de Weight
		self.w.boxFiltro.lblWeight = vanilla.TextBox((10, 25, 100, 20), "Weight Classes:", sizeStyle="small")
		self.w.boxFiltro.listWeight = vanilla.List(
			(10, 45, 220, 80),
			self.weights,
			selectionCallback=self.atualizar_filtro_e_regras,
			allowsMultipleSelection=True,
			allowsEmptySelection=True
		)
		
		# Lista de Width
		self.w.boxFiltro.lblWidth = vanilla.TextBox((250, 25, 100, 20), "Width Classes:", sizeStyle="small")
		self.w.boxFiltro.listWidth = vanilla.List(
			(250, 45, -10, 80),
			self.widths,
			selectionCallback=self.atualizar_filtro_e_regras,
			allowsMultipleSelection=True,
			allowsEmptySelection=True
		)

		self.w.boxFiltro.lblFeedback = vanilla.TextBox((10, 133, -10, 20), "Instâncias encontradas: 0", sizeStyle="small")

		# --- TABELA DE MAPEAMENTO (DUAS COLUNAS) ---
		column_descriptions = [
			{"title": "Glifo Original", "key": "original", "editable": True},
			{"title": "Glifo Substituto", "key": "substituto", "editable": True}
		]
		
		self.w.tabela = vanilla.List(
			(10, 180, -10, -110),
			[],
			columnDescriptions=column_descriptions,
			doubleClickCallback=self.tabela_duplo_clique,
			editCallback=self.tabela_editada
		)

		# --- BOTÕES DE CONTROLE DA TABELA ---
		self.w.btnAdicionar = vanilla.Button((10, -100, 100, 20), "➕ Adicionar", sizeStyle="small", callback=self.adicionar_linha)
		self.w.btnRemover = vanilla.Button((115, -100, 100, 20), "➖ Remover", sizeStyle="small", callback=self.remover_linha)
		self.w.btnImportar = vanilla.Button((-180, -100, -10, 20), "📂 Importar de Selecionada", sizeStyle="small", callback=self.importar_existente)

		# --- BOTÕES DE AÇÃO ---
		self.w.btnAplicarFiltradas = vanilla.Button((10, -65, -10, 25), "Aplicar às instâncias filtradas", callback=self.aplicar_filtradas)
		self.w.btnAplicarTodas = vanilla.Button((10, -35, -10, 25), "Aplicar a todas as instâncias", callback=self.aplicar_todas)

		# Inicializar com todas as instâncias selecionadas por padrão no filtro
		self.w.boxFiltro.listWeight.setSelection(range(len(self.weights)))
		self.w.boxFiltro.listWidth.setSelection(range(len(self.widths)))

		self.atualizar_filtro_e_regras()
		self.w.open()

	def obter_valor_eixo(self, inst, axis_index, fallback_index=0):
		"""Retorna o valor numérico inteiro do eixo da instância tratando erros de NoneType."""
		if not hasattr(inst, "axes") or inst.axes is None:
			return 0
		
		try:
			val = None
			if axis_index is not None and axis_index < len(inst.axes):
				val = inst.axes[axis_index]
			elif fallback_index < len(inst.axes):
				val = inst.axes[fallback_index]
			
			if val is not None:
				return int(val)
		except Exception:
			pass
		return 0

	def obter_instancias_filtradas(self):
		"""Retorna a lista de instâncias baseando-se nas múltiplas seleções de Weight e Width."""
		# Obter os índices selecionados nas listas de filtros
		sel_weights_idx = self.w.boxFiltro.listWeight.getSelection()
		sel_widths_idx = self.w.boxFiltro.listWidth.getSelection()

		# Se nada estiver selecionado, tratamos como se tudo estivesse ativo (ou nenhuma)
		selected_weights = [self.weights[i] for i in sel_weights_idx] if sel_weights_idx else self.weights
		selected_widths = [self.widths[i] for i in sel_widths_idx] if sel_widths_idx else self.widths
		
		instancias_filtradas = []
		for inst in self.font.instances:
			inst_weight = str(self.obter_valor_eixo(inst, self.weight_axis_index, fallback_index=0))
			inst_width = str(self.obter_valor_eixo(inst, self.width_axis_index, fallback_index=1))

			match_weight = (inst_weight in selected_weights)
			match_width = (inst_width in selected_widths)
			
			if match_weight and match_width:
				instancias_filtradas.append(inst)
		return instancias_filtradas

	def atualizar_filtro_e_regras(self, sender=None):
		"""Atualiza as regras da tabela lendo os parâmetros existentes nas instâncias filtradas."""
		filtradas = self.obter_instancias_filtradas()
		self.w.boxFiltro.lblFeedback.set(f"Instâncias que correspondem ao filtro: {len(filtradas)}")

		regras_detectadas = {}
		
		# Busca em lote pelas regras existentes nas instâncias correspondentes
		for inst in filtradas:
			param = inst.customParameters["Rename Glyphs"]
			if param:
				linhas = param.split("\n") if isinstance(param, str) else param
				for linha in list(linhas):
					if "=" in str(linha):
						try:
							orig, dest = str(linha).split("=")
							regras_detectadas[orig.strip()] = dest.strip()
						except ValueError:
							continue
		
		# Converte as regras coletadas e injeta na tabela Vanilla
		itens_tabela = [{"original": orig, "substituto": dest} for orig, dest in regras_detectadas.items()]
		self.w.tabela.set(itens_tabela)

	def adicionar_linha(self, sender):
		self.w.tabela.append({"original": "novo.glifo", "substituto": "novo"})

	def remover_linha(self, sender):
		selecionados = self.w.tabela.getSelection()
		if selecionados:
			for idx in reversed(selecionados):
				self.w.tabela.removeAt(idx)

	def tabela_duplo_clique(self, sender):
		pass

	def tabela_editada(self, sender):
		pass

	def importar_existente(self, sender):
		"""Força a importação das regras de uma instância selecionada na barra lateral (Exports)."""
		selected_insts = self.font.selectedInstances
		if not selected_insts:
			print("⚠️ Selecione uma instância no painel de Font Info > Exports para importar as regras.")
			return
		
		inst = selected_insts[0]
		param = inst.customParameters["Rename Glyphs"]
		if not param:
			print(f"⚠️ A instância '{inst.name}' não possui o parâmetro 'Rename Glyphs'.")
			return
		
		novos_itens = []
		linhas = param.split("\n") if isinstance(param, str) else param
			
		for linha in list(linhas):
			if "=" in str(linha):
				orig, dest = str(linha).split("=")
				novos_itens.append({"original": orig.strip(), "substituto": dest.strip()})
		
		if novos_itens:
			self.w.tabela.set(novos_itens)
			print(f"📂 {len(novos_itens)} regras importadas com sucesso da instância '{inst.name}'.")

	def obter_regras_formatadas(self):
		"""Formata as linhas da tabela para o padrão exigido pelo Glyphs."""
		regras = []
		for item in self.w.tabela.get():
			orig = item["original"].strip()
			subst = item["substituto"].strip()
			if orig and subst:
				regras.append(f"{orig}={subst}")
		return regras

	def aplicar_regras_nas_instancias(self, instancias):
		regras = self.obter_regras_formatadas()
		if not regras:
			print("❌ A tabela de mapeamento está vazia. Adicione regras antes de aplicar.")
			return
		
		self.font.disableUpdateInterface()
		try:
			for inst in instancias:
				inst.customParameters["Rename Glyphs"] = regras
				print(f"✅ 'Rename Glyphs' atualizado na instância: {inst.name}")
		finally:
			self.font.enableUpdateInterface()
		
		Glyphs.showNotification("Rename Glyphs Atualizado", f"Aplicado com sucesso a {len(instancias)} instância(s).")

	def aplicar_filtradas(self, sender):
		filtradas = self.obter_instancias_filtradas()
		if not filtradas:
			print("⚠️ Nenhuma instância atende aos filtros definidos.")
			return
		self.aplicar_regras_nas_instancias(filtradas)

	def aplicar_todas(self, sender):
		all_insts = self.font.instances
		if not all_insts:
			print("⚠️ Nenhuma instância encontrada no arquivo de fonte.")
			return
		self.aplicar_regras_nas_instancias(all_insts)

# Executar a Interface
RenameGlyphsBatchEditor()