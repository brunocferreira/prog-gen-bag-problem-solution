# Genoma como solução.
""" 
`Genome`: Um genoma é a representação de uma solução para o problema. Neste caso, um genoma é representado como uma lista de 0s e 1s.
`Population`: Uma população é um conjunto de genomas. O algoritmo genético trabalha com uma população de soluções em vez de uma única solução.
`FitnessFunc`: Uma função de fitness é usada para avaliar a qualidade de cada solução (genoma) na população. A função recebe um genoma como argumento e retorna um valor inteiro representando o valor de fitness desse genoma. Quanto maior o valor de fitness, melhor a solução.
`PopulateFunc`: Uma função de população é usada para gerar a população inicial do algoritmo genético. A função não recebe argumentos e retorna uma população inicial de genomas.
`SelectionFunc`: Uma função de seleção é usada para selecionar os genomas pais para reprodução. A função recebe uma população e uma função de fitness como argumentos e retorna um par de genomas selecionados para reprodução.
`CrossoverFunc`: Uma função de crossover é usada para realizar o crossover (recombinação) entre os genomas pais para criar novos genomas filhos. A função recebe dois genomas pais como argumentos e retorna um par de genomas filhos criados pelo crossover entre os pais.
`MutationFunc`: Uma função de mutação é usada para aplicar mutação aos genomas filhos. A mutação é um operador que introduz pequenas alterações aleatórias nos genomas para manter a diversidade na população. A função recebe um genoma como argumento e retorna um novo genoma criado pela aplicação da mutação ao genoma original.
`Thing`: Um objeto Thing representa uma coisa com nome, valor e peso. É usado como exemplo em algumas das funções definidas anteriormente.
 """
# --- Libraries ---#
from typing import List, Callable, Tuple
import time
from random import choices, randint, randrange, random
from functools import partial
from collections import namedtuple
import os
os.system('')  # habilita o suporte a sequências de escape ANSI no Windows

# --- Attributes ---#
Genome = List[int]  # Um genoma é representado como uma lista de 0s e 1s
# Uma população é representada como uma lista de genomas
Population = List[Genome]
# Uma função de fitness recebe um genoma e retorna um valor inteiro representando o valor de fitness desse genoma
FitnessFunc = Callable[[Genome], int]
# Uma função de população não recebe argumentos e retorna uma população inicial de genomas
PopulateFunc = Callable[[], Population]
# Uma função de seleção recebe uma população e uma função de fitness e retorna um par de genomas selecionados para reprodução
SelectionFunc = Callable[[Population, FitnessFunc], Tuple[Genome, Genome]]
# Uma função de crossover recebe dois genomas pais e retorna um par de genomas filhos criados pelo crossover entre os pais
CrossoverFunc = Callable[[Genome, Genome], Tuple[Genome, Genome]]
# Uma função de mutação recebe um genoma e retorna um novo genoma criado pela aplicação de mutação ao genoma original
MutationFunc = Callable[[Genome], Genome]
# Um objeto Thing é representado como uma tupla nomeada com campos 'name', 'value' e 'weight'
Thing = namedtuple('Thing', ['name', 'value', 'weight'])

things = [
    Thing('Laptop', 500, 2200),
    Thing('Headphones', 150, 160),
    Thing('Coffe Mug', 60, 350),
    Thing('Notepad', 40, 333),
    Thing('Water Bottle', 30, 192),
]
more_things = [
    Thing('Apple',  4,    7),
    Thing('Mints',  5,    25),
    Thing('Socks',  10,    38),
    Thing('Tissues',  15,    80),
    Thing('Phone',  500,    200),
    Thing('Baseball Cap',  100,    70),
] + things


WEIGHT_TARGET = 1310
STOP_GENERATE = 100


# --- Methods ---#
def generate_genome(length: int) -> Genome:
    """
    Gera um genoma aleatório de comprimento especificado.

    Esta função usa a função `choices` do módulo `random` para gerar uma lista de 0s e 1s de comprimento especificado. Cada elemento da lista é escolhido aleatoriamente com igual probabilidade.

    Parâmetros:
    \n\t`length (int)`: O comprimento do genoma a ser gerado.

    Retorno:
    \n\t`Genome(List[int])`: Uma lista de 0s e 1s representando o genoma gerado.

    Exemplo:
    >>> generate_genome(5)
    [0, 1, 0, 1, 1]
    """
    return choices([0, 1], k=length)


def generate_population(size: int, genome_length: int) -> Population:
    """
    Gera uma população de genomas aleatórios.

    Esta função usa a função `generate_genome` para gerar uma população de genomas aleatórios de comprimento especificado. A população é representada como uma lista de genomas, onde cada genoma é uma lista de 0s e 1s.

    Parâmetros:
    \n\t`size (int)`: O tamanho da população a ser gerada.
    \n\t`genome_length (int)`: O comprimento de cada genoma na população.

    Retorno:
    \n\t`Population[List[int]]`: Uma lista de genomas representando a população gerada.

    Exemplo:
    >>> generate_population(3, 4)
    [[0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]]

    """
    return [generate_genome(genome_length) for _ in range(size)]


def fitness(genome: Genome, things: List[Thing], weight_limit: int) -> int:
    """
    Calcula o valor de fitness de um genoma dado uma lista de coisas e um limite de peso.

    Esta função recebe um genoma (representado como uma lista de 0s e 1s), uma lista de coisas (cada coisa é um dicionário com chaves 'weight' e 'value') e um limite de peso. A função calcula o valor total das coisas selecionadas pelo genoma (onde um 1 na posição i indica que a coisa i foi selecionada) e verifica se o peso total das coisas selecionadas não excede o limite de peso. Se o peso total exceder o limite de peso, a função retorna 0 para indicar que essa é uma solução inválida. Caso contrário, a função retorna o valor total das coisas selecionadas.

    Parâmetros:
    \n\t`genome (List[int])`: O genoma a ser avaliado. 
    \n\t`things (List[Thing])`: A lista de coisas disponíveis. 
    \n\t`weight_limit (int)`: O limite de peso máximo permitido.

    Retorno:
    \n\t`int`: O valor de fitness do genoma. Se o peso total das coisas selecionadas exceder o limite de peso, retorna 0 para indicar uma solução inválida. Caso contrário, retorna o valor total das coisas selecionadas.

    Exemplo:
    >>> things = [{'weight': 1, 'value': 10}, {'weight': 2, 'value': 20}, {'weight': 3, 'value': 30}]
    >>> genome = [1, 0, 1]
    >>> weight_limit = 3
    ...
    >>> fitness(genome, things, weight_limit)
    40

    """
    if len(genome) != len(things):
        raise ValueError("genome e things possuem o mesmo tamanho")

    weight = 0
    value = 0

    for i, thing in enumerate(things):
        if genome[i] == 1:
            weight += thing.weight
            value += thing.value

            if weight > weight_limit:
                return 0  # porque essa solução é inválida

    return value  # porque essa é uma solução válida


def selection_pair(population: Population, fitness_func: FitnessFunc) -> Population:
    """
    Seleciona um par de genomas da população usando o método da roleta.

    Esta função usa a função `choices` do módulo `random` para selecionar aleatoriamente dois genomas da população com probabilidade proporcional ao seu valor de fitness. O valor de fitness de cada genoma é calculado usando a função `fitness_func` fornecida.

    Parâmetros:
    \n\t`population (Population[List[int]])`: A população de genomas.
    \n\t`fitness_func (FitnessFunc[List[int], int]))`: A função de fitness usada para calcular o valor de fitness de cada genoma.

    Retorno:
    \n\t`Population(List[int])`: Uma lista contendo dois genomas selecionados da população.

    Exemplo:
    >>> population = [[0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]]
    >>> def fitness_func(genome):
    ...     return sum(genome)
    ...
    >>> selection_pair(population, fitness_func)
    [[0, 1, 0, 1], [1, 1, 0, 0]]

    """
    return choices(
        population=population,
        weights=[fitness_func(genome) for genome in population],
        k=2
    )


def single_point_crossover(a: Genome, b: Genome) -> Tuple[Genome, Genome]:
    """
    Realiza um crossover de ponto único entre dois genomas.

    Esta função recebe dois genomas (representados como listas de 0s e 1s) e realiza um crossover de ponto único entre eles. Isso significa que um ponto de corte aleatório é escolhido ao longo do comprimento dos genomas e as partes à esquerda e à direita desse ponto são trocadas entre os dois genomas para criar dois novos genomas.

    Parâmetros:
    \n\t`a (Genome(List[int]))`: O primeiro genoma.
    \n\t`b (Genome(List[int]))`: O segundo genoma.

    Retorno:
    \n\t`Tuple[Genome(List[int]), Genome(List[int])`: Um par de novos genomas criados pelo crossover de ponto único.

    Exemplo:
    >>> a = [0, 1, 0, 1]
    >>> b = [1, 1, 0, 0]
    >>> single_point_crossover(a, b)
    ([0, 1, 0, 0], [1, 1, 0, 1])
    """
    if len(a) != len(b):
        raise ValueError("Os genomas possuem o mesmo tamanho")

    length = len(a)
    if length < 2:
        return a, b

    p = randint(1, length - 1)
    return a[0:p] + b[p:], b[0:p] + a[p:]


def mutation(genome: Genome, num: int = 1, probability: float = 0.5) -> Genome:
    """
    Realiza uma mutação em um genoma.

    Esta função recebe um genoma (representado como uma lista de 0s e 1s) e realiza uma mutação nele. Isso significa que um número especificado de bits no genoma são selecionados aleatoriamente e invertidos (de 0 para 1 ou de 1 para 0) com uma probabilidade especificada.

    Parâmetros:
    \n\t`genome (Genome(List[int]))`: O genoma a ser mutado.
    \n\t`num (int)`: O número de bits a serem mutados. O padrão é 1.
    \n\t`probability (float)`: A probabilidade de cada bit selecionado ser invertido. O padrão é 0.5.

    Retorno:
    \n\t`Genome(List[int])`: O genoma mutado.

    Exemplo:
    >>> genome = [0, 1, 0, 1]
    >>> mutation(genome, num=2, probability=0.5)
    [1, 1, 0, 1]
    """
    for _ in range(num):
        index = randrange(len(genome))
        genome[index] = genome[index] if random(
        ) > probability else abs(genome[index] - 1)  # do contrário, retorne o valor escalar

    return genome


def run_evolution(
    population_func: PopulateFunc,
    fitness_func: FitnessFunc,
    fitness_limit: int,
    selection_func: SelectionFunc = selection_pair,
    crossover_func: CrossoverFunc = single_point_crossover,
    mutation_func: MutationFunc = mutation,
    generation_limit: int = 100
) -> Tuple[Population, int]:
    """
    Executa um algoritmo genético para evoluir uma população de genomas.

    Esta função recebe várias funções como argumentos que definem como a população inicial é gerada, como o valor de fitness de cada genoma é calculado, como os genomas são selecionados para reprodução, como o crossover é realizado entre os genomas pais e como a mutação é aplicada aos genomas filhos. A função executa o algoritmo genético por um número especificado de gerações ou até que um genoma com um valor de fitness acima de um limite especificado seja encontrado.

    Parâmetros:
    \n\t`population_func (PopulateFunc[[], Population[List[int]]])`: A função usada para gerar a população inicial.
    \n\t`fitness_func (FitnessFunc[Genome(List[int]), int])`: A função usada para calcular o valor de fitness de cada genoma.
    \n\t`fitness_limit (int)`: O limite de fitness que um genoma deve atingir para interromper a evolução.
    \n\t`selection_func (SelectionFunc[[Population[List[int]], FitnessFunc[Genome(List[int]), int]], Tuple[Genome(List[int]), Genome(List[int]))`: A função usada para selecionar os genomas pais para reprodução. O padrão é `selection_pair`.
    \n\t`crossover_func (CrossoverFunc[[Genome(List[int]), Genome(List[int])], Tuple[Genome(List[int]), Genome(List[int])]])`: A função usada para realizar o crossover entre os genomas pais. O padrão é `single_point_crossover`.
    \n\t`mutation_func (MutationFunc[Genome(List[int]), Genome(List[int])])`: A função usada para aplicar mutação aos genomas filhos. O padrão é `mutation`.
    \n\t`generation_limit (int)`: O número máximo de gerações a serem executadas. O padrão é 100.

    Retorno:
    \n\t`Tuple [Population[List[int]], int]]`: Um par contendo a população final e o número de gerações executadas.

    Exemplo:
    >>> def population_func():
    ...     return [[0, 1, 0, 1], [1, 1, 0, 0], [0, 0, 1, 1]]
    ...
    >>> def fitness_func(genome):
    ...     return sum(genome)
    ...
    >>> run_evolution(population_func, fitness_func, fitness_limit=3)
    ([[1, 1, 1, 1], [1, 1, 1, 0], [1, 1, 0, 1], [0, 1, 0, 1], [0, 0, 1, 1], [1, 1, 0, 0]], 2)
    """
    population = population_func()

    for i in range(generation_limit):
        population = sorted(
            population,
            key=lambda genome: fitness_func(genome),
            reverse=True
        )

        if fitness_func(population[0]) >= fitness_limit:
            break

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):
            parents = selection_func(population, fitness_func)
            offspring_a, offspring_b = crossover_func(parents[0], parents[1])
            offspring_a = mutation_func(offspring_a)
            offspring_b = mutation_func(offspring_b)
            next_generation += [offspring_a, offspring_b]

        population = next_generation

    population = sorted(
        population,
        key=lambda genome: fitness_func(genome),
        reverse=True
    )

    return population, i


start = time.time()
population, generations = run_evolution(
    population_func=partial(
        generate_population, size=10, genome_length=len(more_things)
    ),
    fitness_func=partial(
        fitness, things=more_things, weight_limit=3000
    ),
    fitness_limit=WEIGHT_TARGET,
    generation_limit=STOP_GENERATE
)
end = time.time()


def genome_to_things(genome: Genome, things: List[Thing]) -> List[Thing]:
    """
    Converte um genoma em uma lista de nomes de coisas selecionadas.

    Esta função recebe um genoma (representado como uma lista de 0s e 1s) e uma lista de coisas (cada coisa é um objeto com um atributo `name`) e retorna uma lista de nomes das coisas selecionadas pelo genoma (onde um 1 na posição i indica que a coisa i foi selecionada).

    Parâmetros:
    \n\t`genome (Genome(List[int]))`: O genoma a ser convertido.
    \n\t`things (List[Thing])`: A lista de coisas disponíveis.

    Retorno:
    \n\t`List[str]`: Uma lista de nomes das coisas selecionadas pelo genoma.

    Exemplo:
    >>> things = [Thing(name='Lápis'), Thing(name='Caneta'), Thing(name='Borracha')]
    >>> genome = [1, 0, 1]
    ...
    >>> genome_to_things(genome, things)
    ['Lápis', 'Borracha']

    """
    result = []
    for i, thing in enumerate(things):
        if genome[i] == 1:
            result += [thing.name]

    return result


print(f'nº de gerações até a solução: \033[33m{generations}\033[0m.')
print(f'o tempo para encontrar a solução: \033[36m{end - start}\033[0ms.')
print(
    f'a melhor solução: \033[32m{genome_to_things(population[0], more_things)}\033[0m.'
)
