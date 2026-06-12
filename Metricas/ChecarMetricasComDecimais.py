#MenuTitle: Verificar Métricas com Decimais
# -*- coding: utf-8 -*-
from __future__ import division, print_function, unicode_literals
__doc__ = """
Abre janela com glifos que tenham métricas em decimais.
Com interface para escolher master atual ou todas as masters.
"""

import vanilla
from GlyphsApp import *

class VerificarMetricas:
    def __init__(self):
        self.font = Font

        # --- Dimensões da janela ---
        self.w = vanilla.FloatingWindow(
            (400, 160),
            "Verificar Métricas com Decimais"
        )

        # --- Lista de masters para o dropdown ---
        self.master_names = [m.name for m in self.font.masters]

        # --- Checkbox: todas as masters ---
        self.w.checkbox_todas = vanilla.CheckBox(
            (20, 20, -20, 22),
            "Verificar todas as masters",
            value=False,
            callback=self.toggle_masters
        )

        # --- Label + Dropdown para master específica ---
        self.w.label_master = vanilla.TextBox(
            (20, 55, 120, 22),
            "Master:"
        )

        self.w.dropdown_master = vanilla.PopUpButton(
            (90, 52, -20, 22),
            self.master_names
        )

        # --- Seleciona a master atual no dropdown ---
        master_atual = self.font.selectedFontMaster
        if master_atual and master_atual.name in self.master_names:
            self.w.dropdown_master.set(
                self.master_names.index(master_atual.name)
            )

        # --- Divisória ---
        self.w.line = vanilla.HorizontalLine(
            (20, 90, -20, 1)
        )

        # --- Botão executar ---
        self.w.botao = vanilla.Button(
            (20, 108, -20, 32),
            "Verificar",
            callback=self.executar
        )

        self.w.open()

    def toggle_masters(self, sender):
        # Habilita ou desabilita o dropdown conforme o checkbox
        todas = self.w.checkbox_todas.get()
        self.w.dropdown_master.enable(not todas)
        self.w.label_master.enable(not todas)

    def executar(self, sender):
        todas = self.w.checkbox_todas.get()

        if todas:
            masters = self.font.masters
        else:
            idx = self.w.dropdown_master.get()
            masters = [self.font.masters[idx]]

        glifos_com_erro = {}  # { glyph.name: [masters com erro] }

        for master in masters:
            print("=" * 50)
            print("Buscando na master: %s" % master.name)
            print("-" * 50)

            for glyph in self.font.glyphs:
                layer = glyph.layers[master.id]

                lsb   = layer.LSB
                rsb   = layer.RSB
                width = layer.width

                if (lsb % 1 != 0) or (rsb % 1 != 0) or (width % 1 != 0):
                    info = "Glifo: %-20s | LSB: %-8s | RSB: %-8s | Width: %-8s" % (
                        glyph.name, lsb, rsb, width
                    )
                    print(info)

                    if glyph.name not in glifos_com_erro:
                        glifos_com_erro[glyph.name] = []
                    glifos_com_erro[glyph.name].append(master.name)

        print("-" * 50)

        if glifos_com_erro:
            print("⚠️  %d glifo(s) encontrados com métricas decimais." % len(glifos_com_erro))

            if todas:
                for nome, masters_com_erro in glifos_com_erro.items():
                    print("  • %s → masters: %s" % (nome, ", ".join(masters_com_erro)))

            tab_string = "/" + "/".join(glifos_com_erro.keys())
            self.font.newTab(tab_string)
            print("✅ Aba aberta com os glifos encontrados.")
        else:
            print("✅ Nenhum glifo com métricas decimais encontrado. Tudo limpo!")

        self.w.close()

VerificarMetricas()
