import matplotlib.pyplot as plt
import numpy as np
import requests
import pwinput

token = ""
usuarioNome = ""

def titulo(texto, sublinhado="-"):
  print()
  print(texto)
  print(sublinhado*40)

def login():
  titulo("Login do Usuário")

  email = input("E-mail: ")
  senha = pwinput.pwinput("Senha.: ")

  response = requests.post("http://localhost:3000/login", 
    json={"email": email, "senha": senha}
  )

  if response.status_code != 200:
    print("-" * 40)
    print("Erro... Login ou Senha inválidos")
    return
  
  dados = response.json()

  # para indicar que a variável aqui atribuída é a global 
  # (e não uma nova variável criada nesta função)
  global token 
  global usuarioNome
  token = dados['token']
  usuarioNome = dados['nome']
  print(f"Bem-vindo ao sistema: {usuarioNome}")

def inclusao():
  titulo("Inclusão de Automóveis")

  if token == "":
    print("Erro... Você deve logar-se primeiro")
    return

  modelo = input("Modelo do Veículo: ")
  marca = input("Fabricante: ")
  ano = int(input("Ano de Fabricação: "))
  custo = float(input("Custo Mensal..: "))
  passageiros = int(input("Nº de passageiros: "))

  response = requests.post("http://localhost:3000/carros", 
    json={"modelo": modelo, "marca": marca, "ano": ano, "custo_mensal": custo, "QtdPassageiros":passageiros},
    headers={"Authorization": f"Bearer {token}"}
  )

  if response.status_code == 201:
    dados = response.json()
    print("-" * 40)
    print(f"Veículo cadastrado com sucesso! Código: {dados['id']}")
    print("-" * 40)
  else:
    print("-" * 40)
    print(f"Não foi possível cadastrar o veículo informado!")
    print("-" * 40)

# ----------------------------------------------------------------------------------------

def listar_veiculos():
    titulo("Listagem de Veículos Cadastrados")

    if token == "":
        print("Erro... Você deve logar-se primeiro")
        return

    response = requests.get("http://localhost:3000/carros", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print("Erro... Não foi possível obter a lista de veículos")
        return

    dados = response.json()

    for carro in dados:
        print(f"Código: {carro['id']}")
        print(f"Modelo: {carro['modelo']}")
        print(f"Fabricante: {carro['marca']}")
        print(f"Ano: {carro['ano']}")
        print(f"Capacidade: {carro['QtdPassageiros']} pessoas")
        print(f"Custo Mensal: {carro['custo_mensal']}")
        print("-" * 40)

# ----------------------------------------------------------------------------------------


def alterar_veiculo():
    titulo("Alteração de Dados de Veículo")

    if token == "":
        print("Erro... Você deve logar-se primeiro")
        return

    id = int(input("Digite o código do veículo que deseja alterar: "))
    print("-" * 40)

    # Verifica se o veículo existe
    response = requests.get(f"http://localhost:3000/carros/{id}", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print("-" * 40)
        print(f"Erro ao obter o veículo com id {id}. Status code: {response.status_code}")
        return

    carro = response.json()

    # Solicita os novos dados para alteração
    novo_modelo = input(f"Novo Modelo ({carro['modelo']}): ").strip() or carro['modelo']
    nova_marca = input(f"Nova Fabricante ({carro['marca']}): ").strip() or carro['marca']
    novo_ano = input(f"Novo Ano de Fabricação ({carro['ano']}): ").strip() or carro['ano']
    nova_capacidade = input(f"Nova capacidade passageiros ({carro['QtdPassageiros']}): ").strip() or carro['QdtPassageiros']
    novo_custo = input(f"Novo Custo Mensal ({carro['custo_mensal']}): ").strip() or carro['custo_mensal']

    # Realiza a atualização na API
    response = requests.put(f"http://localhost:3000/carros/{id}",
                            json={"modelo": novo_modelo, "marca": nova_marca, "ano": int(novo_ano), "QtdPassageiros": int(nova_capacidade),  "custo_mensal": float(novo_custo)},
                            headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        print("-" * 40)
        print("Dados do veículo atualizados com sucesso")
    else:
        print("-" * 40)
        print("Não foi possível atualizar os dados do veículo")


# ----------------------------------------------------------------------------------------


def excluir_veiculo():
    titulo("Exclusão de Veículo")

    if token == "":
        print("Erro... Você deve logar-se primeiro")
        return

    # Obtém o ID do carro que deseja excluir
    id = int(input("Digite o código do veículo que deseja excluir: "))

    # Verifica se o veículo existe antes de excluir
    response = requests.get(f"http://localhost:3000/carros/{id}", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print(f"Veículo com ID {id} não encontrado")
        return

    carro = response.json()

    # Mostra os dados do carro antes de confirmar a exclusão
    print("-" * 40)
    print("Detalhes do Carro:")
    print(f"ID: {carro['id']}")
    print(f"Modelo: {carro['modelo']}")
    print(f"Fabricante: {carro['marca']}")
    print(f"Ano: {carro['ano']}")
    print(f"Capacidade: {carro['QtdPassageiros']} pessoas")
    print(f"Custo Mensal: {carro['custo_mensal']}")
    print("-" * 40)

    # Confirmação com o usuário
    confirmacao = input(f"Deseja realmente excluir o carro com ID {id}? (s/n): ").strip().lower()

    if confirmacao != 's':
        print("-" * 40)
        print("Exclusão cancelada pelo usuário")
        return

    # Realiza a exclusão na API
    response = requests.delete(f"http://localhost:3000/carros/{id}", headers={"Authorization": f"Bearer {token}"})

    if response.status_code == 200:
        print("-" * 40)
        print(f"Carro com ID {id} foi excluído com sucesso")
    else:
        print("-" * 40)
        print(f"Não foi possível excluir o carro com ID {id}. Status code: {response.status_code}")


# ----------------------------------------------------------------------------------------

def carros_por_marca():
    titulo("Contagem de Carros por Marca")

    if token == "":
        print("Erro... Você deve logar-se primeiro")
        return

    # Faz a requisição para obter a contagem de carros por marca
    response = requests.get("http://localhost:3000/carros/contagem/marcas", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print(f"Erro ao obter a contagem de carros por marca. Status code: {response.status_code}")
        return

    contagem = response.json()

    # Exibe a contagem de carros por marca
    for item in contagem:
        print(f"Marca: {item['marca']} - Quantidade: {item['_count']['marca']}")

    print("-" * 40)

# ----------------------------------------------------------------------------------------
def grafico_geral():
    titulo("Comparação de Custos Mensais por Modelo de Veículo")

    if token == "":
        print("Erro... Você deve logar-se primeiro")
        return

    response = requests.get("http://localhost:3000/carros", headers={"Authorization": f"Bearer {token}"})

    if response.status_code != 200:
        print("Erro... Não foi possível obter a lista de veículos")
        return

    dados = response.json()

    modelos = []
    custos_mensais = []

    for carro in dados:
        modelos.append(carro['modelo'])
        custos_mensais.append(carro['custo_mensal'])

    # Cria o gráfico de barras
    fig, ax = plt.subplots()
    ax.bar(modelos, custos_mensais, color='blue')

    ax.set_xlabel('Modelo de Veículo')
    ax.set_ylabel('Custo Mensal')
    ax.set_title('Comparação de Custos Mensais por Modelo de Veículo')
    ax.set_xticklabels(modelos, rotation=45, ha='right')

    plt.tight_layout()
    plt.show()

# ----------------------------------- Programa Principal
while True:
  if token: 
    titulo(f"Locadora AlugaCar Automóveis - Usuário {usuarioNome}", "=")
  else:
    titulo("Locadora AlugaCar Automóveis", "=")
  print("1. Fazer Login")
  print("2. Incluir Veículo")
  print("3. Listar Veículos")
  print("4. Alterar Dados de Veículo")
  print("5. Excluir Carro")
  print("6. Listar carros por montadora")
  print("7. Gráfico Relacionando Custo dos Veículos")
  print("8. Finalizar")
  opcao = int(input("Opção: "))
  if opcao == 1:
    login()
  elif opcao == 2:
    inclusao()
  elif opcao == 3:
    listar_veiculos()
  elif opcao == 4:
   alterar_veiculo()
  elif opcao ==5:
    excluir_veiculo() 
  elif opcao ==6:
    carros_por_marca() 
  elif opcao == 7:
    grafico_geral()
  else:
    break
