
import datetime
import time
import random

VELOCIDADE_MEDIA_KMH = 80  # velocidade média padrão para cálculo de tempo (Velocidade em km/h dos caminhões nas estradas brasileiras)

class Entrega:
    def __init__(self, id_entrega, destino, prazo_maximo, peso_carga, observacao=""):
        self.id_entrega = id_entrega
        self.destino = destino
        self.prazo_maximo = prazo_maximo
        self.peso_carga = peso_carga
        self.observacao = observacao

class Caminhao:
    def __init__(self, id_caminhao, capacidade_maxima_carga, limite_horas_operacao_dia, centro_distribuicao_base):
        self.id_caminhao = id_caminhao
        self.capacidade_maxima_carga = capacidade_maxima_carga
        self.limite_horas_operacao_dia = limite_horas_operacao_dia
        self.centro_distribuicao_base = centro_distribuicao_base
        self.carga_atual = 0
        self.horas_operadas_hoje = 0
        self.rota_atual = []

class CentroDistribuicao:
    def __init__(self, id_cd, nome_curto, nome_tabela):
        self.id_cd = id_cd
        self.nome_curto = nome_curto
        self.nome_tabela = nome_tabela
        self.caminhoes_disponiveis = []

class GrafoRotas:
    def __init__(self):
        self.adjacencia = {}

    def adicionar_aresta(self, origem_cd_tabela, destino_capital, distancia_km):
        tempo_estimado = round(distancia_km / VELOCIDADE_MEDIA_KMH, 2)
        if origem_cd_tabela not in self.adjacencia:
            self.adjacencia[origem_cd_tabela] = {}
        self.adjacencia[origem_cd_tabela][destino_capital] = {
            'distancia': distancia_km,
            'tempo_horas': tempo_estimado
        }

    def obter_info_rota_direta(self, origem_cd_tabela, destino_capital):
        return self.adjacencia.get(origem_cd_tabela, {}).get(destino_capital)

def encontrar_cd_mais_proximo_por_peso(destino_capital, centros_distribuicao, grafo):
    melhor_cd = None
    menor_distancia = float('inf')
    melhor_rota_info = None

    for cd in centros_distribuicao:
        info = grafo.obter_info_rota_direta(cd.nome_tabela, destino_capital)
        if info and info['distancia'] < menor_distancia:
            menor_distancia = info['distancia']
            melhor_cd = cd
            melhor_rota_info = info

    return melhor_cd, melhor_rota_info

def otimizar_rotas_para_cd(cd, entregas, grafo, verbose=True):
    entregas_restantes = entregas[:]
    entregas_nao_alocadas = []
    entregas_alocadas = []

    for caminhao in cd.caminhoes_disponiveis:
        caminhao.rota_atual = []
        caminhao.carga_atual = 0
        cidade_atual = cd.nome_tabela

        novas_entregas = []
        for entrega in list(entregas_restantes):
            rota_info = grafo.obter_info_rota_direta(cidade_atual, entrega.destino)
            if not rota_info:
                continue

            if caminhao.carga_atual + entrega.peso_carga <= caminhao.capacidade_maxima_carga:
                caminhao.rota_atual.append(entrega)
                caminhao.carga_atual += entrega.peso_carga
                entregas_restantes.remove(entrega)
                cidade_atual = entrega.destino
                novas_entregas.append(entrega)

        if verbose and caminhao.rota_atual:
            print(f"\n🚚 Caminhão {caminhao.id_caminhao} utilizado (Capacidade: {caminhao.capacidade_maxima_carga}kg)")
            cidade_atual = cd.nome_tabela
            for ent in caminhao.rota_atual:
                rota_info = grafo.obter_info_rota_direta(cidade_atual, ent.destino)
                distancia = rota_info['distancia'] if rota_info else '?'
                tempo = rota_info['tempo_horas'] if rota_info else '?'
                print(f"   → Entrega para {ent.destino} ({ent.peso_carga:.2f}kg)")
                print(f"     Distância: {distancia} km | Tempo estimado: {tempo} horas")
                cidade_atual = ent.destino
            entregas_alocadas.extend(novas_entregas)

    if verbose and entregas_alocadas:
        print(f"\n📦 CD {cd.nome_curto}: {len(entregas_alocadas)} entrega(s)")

    for entrega in entregas_restantes:
        entregas_nao_alocadas.append((entrega, "Sem caminhão disponível"))

    if verbose and entregas_nao_alocadas:
        print(f"\n⚠️ {len(entregas_nao_alocadas)} entrega(s) não alocadas no CD {cd.nome_curto}:")
        for ent, motivo in entregas_nao_alocadas:
            print(f"   🚫 Entrega {ent.id_entrega} para {ent.destino} ({ent.peso_carga}kg) → {motivo}")

def carregar_dados_baseados_na_tabela(): # Criamos 5 CDs fixos
    cds = [
        CentroDistribuicao("CD_BEL", "CD Belém", "Belém (PA)"),
        CentroDistribuicao("CD_REC", "CD Recife", "Recife (PE)"),
        CentroDistribuicao("CD_BSB", "CD Brasília", "Brasília (DF)"),
        CentroDistribuicao("CD_SAO", "CD São Paulo", "São Paulo (SP)"),
        CentroDistribuicao("CD_FLN", "CD Florianópolis", "Florianópolis (SC)")
    ]

    grafo = GrafoRotas() 
    # adicionamos todas as capitais do Brasil
    # e os pesos entre elas
    # Os pesos são realistas sobre a distância entre as capitais em km
    # e o tempo estimado para percorrer essa distância em horas
    dados_pesos = [
    ['Rio Branco (AC)',       3150, 5150, 2670, 3500, 3850],
    ['Maceió (AL)',           2130, 280, 1850, 2200, 2600],
    ['Macapá (AP)',           870, 2200, 2200, 3100, 3400],
    ['Manaus (AM)',           1800, 4300, 3500, 4000, 4500],
    ['Salvador (BA)',         2100, 800, 1450, 1960, 2400],
    ['Fortaleza (CE)',        1600, 800, 2200, 3000, 3400],
    ['Brasília (DF)',         1950, 1650, 0, 1015, 1670],
    ['Vitória (ES)',          2800, 1300, 1230, 880, 1350],
    ['Goiânia (GO)',          2150, 1900, 210, 934, 1570],
    ['São Luís (MA)',         800, 1200, 2100, 2950, 3300],
    ['Cuiabá (MT)',           2940, 2480, 1130, 1410, 1840],
    ['Campo Grande (MS)',     3190, 2850, 1130, 1010, 1140],
    ['Belo Horizonte (MG)',   2820, 1550, 710, 580, 1020],
    ['Belém (PA)',            0, 2100, 1950, 2930, 3200],
    ['João Pessoa (PB)',      2030, 120, 2120, 2660, 2960],
    ['Curitiba (PR)',         3190, 2670, 1370, 410, 300],
    ['Recife (PE)',           2100, 0, 2110, 2670, 2970],
    ['Teresina (PI)',         950, 1190, 1250, 2450, 2700],
    ['Rio de Janeiro (RJ)',   3240, 1860, 1160, 430, 1140],
    ['Natal (RN)',            2180, 290, 2240, 2820, 3000],
    ['Porto Alegre (RS)',     3860, 3460, 2030, 1110, 480],
    ['Porto Velho (RO)',      4000, 4200, 2170, 2300, 2700],
    ['Boa Vista (RR)',        6100, 6100, 4300, 5000, 5400],
    ['Florianópolis (SC)',    3520, 3250, 1670, 705, 0],
    ['São Paulo (SP)',        2930, 2670, 1015, 0, 705],
    ['Aracaju (SE)',          2200, 300, 1700, 2100, 2560],
    ['Palmas (TO)',           2080, 1590, 970, 1400, 1800],
] # no momento do teste é necessário digitar o nome da capital junto com a sigla do estado
    # Exemplo: "São Paulo (SP)" ou "Florianópolis (SC)", completo como está no array acima

    indice = {
        "Belém (PA)": 1,
        "Recife (PE)": 2,
        "Brasília (DF)": 3,
        "São Paulo (SP)": 4,
        "Florianópolis (SC)": 5
    }

    for linha in dados_pesos:
        destino = linha[0]
        for cd in cds:
            peso = linha[indice[cd.nome_tabela]]
            grafo.adicionar_aresta(cd.nome_tabela, destino, peso)

    for cd in cds:
        cd.caminhoes_disponiveis = [
            Caminhao(f"{cd.id_cd}_C1", 999, 8, cd.nome_tabela),
            Caminhao(f"{cd.id_cd}_C2", 5999, 8, cd.nome_tabela),
            Caminhao(f"{cd.id_cd}_C3", 9999, 8, cd.nome_tabela)
        ]

    destinos_validos = sorted(set(linha[0] for linha in dados_pesos))
    return cds, grafo, destinos_validos

def benchmark_execucao(cds_base, grafo, capitais_validas):
    print("\n📈 Executando benchmarks de desempenho...")
    for quantidade in [10, 100, 500, 1000]:
        entregas = []
        for i in range(quantidade):
            destino = random.choice(capitais_validas)
            peso = random.uniform(50, 1000)
            prazo = datetime.datetime.now() + datetime.timedelta(days=3)
            entrega = Entrega(f"E{i+1:04}", destino, prazo.strftime("%Y-%m-%d"), peso)
            entregas.append(entrega)

        entregas_por_cd = {}
        for e in entregas:
            cd, _ = encontrar_cd_mais_proximo_por_peso(e.destino, cds_base, grafo)
            if cd:
                entregas_por_cd.setdefault(cd.id_cd, []).append(e)

        cds = []
        for base in cds_base:
            novo_cd = CentroDistribuicao(base.id_cd, base.nome_curto, base.nome_tabela)
            novo_cd.caminhoes_disponiveis = [
                Caminhao(f"{base.id_cd}_C1", 999, 8, base.nome_tabela),
                Caminhao(f"{base.id_cd}_C2", 5999, 8, base.nome_tabela),
                Caminhao(f"{base.id_cd}_C3", 9999, 8, base.nome_tabela)
            ]
            cds.append(novo_cd)

        inicio = time.time()
        for cd in cds:
            if cd.id_cd in entregas_por_cd:
                otimizar_rotas_para_cd(cd, entregas_por_cd[cd.id_cd], grafo, verbose=False)
        fim = time.time()

        print(f"\n🔍 Teste com {quantidade} entregas:")
        print(f"⏱️ Tempo de execução: {fim - inicio:.4f} segundos")
        print("--------------------------------------------------")

if __name__ == "__main__":
    cds, grafo, capitais_validas = carregar_dados_baseados_na_tabela()
    todas_entregas = []

    while True:
        try:
            qtd = int(input("Quantas entregas deseja registrar? (0 para sair): "))
        except:
            break
        if qtd <= 0:
            break

        for i in range(qtd):
            print(f"\nEntrega {i+1}:")
            while True:
                destino = input("Capital destino: ").strip()
                if destino in capitais_validas:
                    break
                print("Destino inválido. Tente novamente.")

            peso = float(input("Peso da carga (kg): ") or "10")
            prazo = datetime.datetime.now() + datetime.timedelta(days=3)
            entrega = Entrega(f"E{len(todas_entregas)+1:03}", destino, prazo.strftime("%Y-%m-%d"), peso)
            todas_entregas.append(entrega)

        cont = input("\nRegistrar mais entregas? (s/N): ").strip().lower()
        if cont != 's':
            break

    print(f"\nTotal de entregas registradas: {len(todas_entregas)}")
    print("\n--- Otimizando rotas por CD ---")

    entregas_por_cd = {}
    for entrega in todas_entregas:
        cd, _ = encontrar_cd_mais_proximo_por_peso(entrega.destino, cds, grafo)
        if cd:
            entregas_por_cd.setdefault(cd.id_cd, []).append(entrega)

    for cd in cds:
        if cd.id_cd in entregas_por_cd:
            otimizar_rotas_para_cd(cd, entregas_por_cd[cd.id_cd], grafo)
        else:
            print(f"⚠️ Nenhuma entrega para {cd.nome_curto}.")

    benchmark_execucao(cds, grafo, capitais_validas)
