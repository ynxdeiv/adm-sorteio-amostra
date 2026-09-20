"""Testes do sorteio. Rodar da raiz: python3 -m unittest discover -s testes -t ."""

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
if str(RAIZ) not in sys.path:
    sys.path.insert(0, str(RAIZ))

from src import dados, sorteio

EXEMPLO = RAIZ / "exemplos" / "exemplo.json"


def participante(numero, lid, papel="membro", nome=""):
    return {"numero": numero, "lid": lid, "papel": papel, "nomeAgenda": nome}


class TestUniverso(unittest.TestCase):
    def test_le_o_exemplo(self):
        self.assertEqual(len(dados.carregarParticipantes(EXEMPLO)), 6)

    def test_remove_repetidos_e_vazios(self):
        universo = dados.elegiveis(
            [
                participante("551", "1"),
                participante("551", "1"),
                participante("", "2"),
                participante("553", ""),
            ],
            "numero",
        )
        self.assertEqual([valor for valor, _ in universo], ["551", "553"])

    def test_filtra_por_papel(self):
        participantes = [
            participante("551", "1", papel="admin"),
            participante("552", "2"),
            participante("553", "3", papel="admin"),
        ]
        self.assertEqual(len(dados.elegiveis(participantes, "numero", "admin")), 2)
        self.assertEqual(len(dados.elegiveis(participantes, "numero")), 3)

    def test_erro_em_json_invalido(self):
        with tempfile.TemporaryDirectory() as pasta:
            ruim = Path(pasta) / "ruim.json"
            ruim.write_text("{isso não é json", encoding="utf-8")
            with self.assertRaises(dados.ErroDeDados):
                dados.carregarParticipantes(ruim)

    def test_erro_quando_arquivo_nao_existe(self):
        with self.assertRaises(dados.ErroDeDados):
            dados.acharJson("/caminho/que/nao/existe.json")


class TestSorteio(unittest.TestCase):
    def setUp(self):
        self.universo = dados.elegiveis(dados.carregarParticipantes(EXEMPLO), "numero")

    def test_sorteia_sem_repetir_e_no_tamanho_pedido(self):
        _, escolhidos = sorteio.sortear(self.universo, 4, seed=1)
        ids = [valor for valor, _ in escolhidos]
        self.assertEqual(len(ids), 4)
        self.assertEqual(len(set(ids)), 4)

    def test_mesma_seed_mesmo_resultado(self):
        _, primeiro = sorteio.sortear(self.universo, 3, seed=42)
        _, segundo = sorteio.sortear(self.universo, 3, seed=42)
        self.assertEqual([v for v, _ in primeiro], [v for v, _ in segundo])

    def test_seed_automatica_e_inteira(self):
        seed, escolhidos = sorteio.sortear(self.universo, 2)
        self.assertIsInstance(seed, int)
        self.assertEqual(len(escolhidos), 2)

    def test_erro_quando_pede_mais_que_o_universo(self):
        with self.assertRaises(ValueError):
            sorteio.sortear(self.universo, len(self.universo) + 1, seed=1)

    def test_erro_quando_pede_zero(self):
        with self.assertRaises(ValueError):
            sorteio.sortear(self.universo, 0, seed=1)

    def test_todo_elegivel_pode_sair(self):
        universo = [(str(indice), {"numero": str(indice)}) for indice in range(10)]
        sorteados = set()
        for seed in range(200):
            _, escolhidos = sorteio.sortear(universo, 1, seed=seed)
            sorteados.add(escolhidos[0][0])
        self.assertEqual(len(sorteados), 10)

    def test_hash_do_universo_depende_da_ordem(self):
        self.assertNotEqual(
            sorteio.hashUniverso([("1", {}), ("2", {})]),
            sorteio.hashUniverso([("2", {}), ("1", {})]),
        )
        self.assertEqual(
            sorteio.hashUniverso([("1", {}), ("2", {})]),
            sorteio.hashUniverso([("1", {}), ("2", {})]),
        )


class TestRegistro(unittest.TestCase):
    def test_registro_traz_seed_hash_e_sorteados(self):
        universo = dados.elegiveis(dados.carregarParticipantes(EXEMPLO), "numero")
        seed, escolhidos = sorteio.sortear(universo, 2, seed=7)
        quando = datetime(2024, 1, 1, tzinfo=timezone.utc)
        registro = sorteio.montarRegistro(
            EXEMPLO, "numero", None, seed, 2, universo, escolhidos, quando
        )
        self.assertEqual(registro["seed"], 7)
        self.assertEqual(registro["universo"], 6)
        self.assertEqual(registro["geradoEm"], "2024-01-01T00:00:00+00:00")
        self.assertEqual(registro["hashUniverso"], sorteio.hashUniverso(universo))
        self.assertEqual(len(registro["sorteados"]), 2)
        for item in registro["sorteados"]:
            self.assertIn("numero", item)
            self.assertIn("nome", item)


class TestLinhaDeComando(unittest.TestCase):
    def rodar(self, *argumentos):
        return subprocess.run(
            [sys.executable, str(RAIZ / "sortear.py"), *argumentos],
            capture_output=True,
            text=True,
            cwd=RAIZ,
        )

    def test_apenas_ids_e_repetivel(self):
        primeira = self.rodar("--json", str(EXEMPLO), "-n", "3", "--seed", "7", "--apenas-ids")
        segunda = self.rodar("--json", str(EXEMPLO), "-n", "3", "--seed", "7", "--apenas-ids")
        self.assertEqual(primeira.returncode, 0)
        self.assertEqual(primeira.stdout, segunda.stdout)
        self.assertEqual(len(primeira.stdout.split()), 3)

    def test_salva_registro(self):
        with tempfile.TemporaryDirectory() as pasta:
            destino = Path(pasta) / "sorteio.json"
            resultado = self.rodar(
                "--json", str(EXEMPLO), "-n", "2", "--seed", "1", "--salvar", str(destino)
            )
            self.assertEqual(resultado.returncode, 0)
            registro = json.loads(destino.read_text(encoding="utf-8"))
            self.assertEqual(registro["seed"], 1)
            self.assertEqual(len(registro["sorteados"]), 2)

    def test_erro_de_uso_sai_com_codigo_2(self):
        resultado = self.rodar("--json", str(EXEMPLO), "-n", "99")
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("elegíveis", resultado.stderr)

    def test_json_inexistente_sai_com_codigo_2(self):
        self.assertEqual(self.rodar("--json", "/nao/existe.json", "-n", "1").returncode, 2)


if __name__ == "__main__":
    unittest.main()
