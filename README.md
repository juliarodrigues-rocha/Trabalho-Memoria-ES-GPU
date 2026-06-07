# 🖥️ Trabalho Prático — Memória, E/S e GPU na Prática

**Disciplina:** Organização e Arquitetura de Computadores
**Curso:** Sistemas de Informação

## 👥 Integrantes

| Nome                     | RA       |
| ------------------------ | -------- |
| Júlia Rodrigues da Rocha | 25005897 |
| Giovana Budri Oliveira   | 25017683 |

---

# 📖 Sobre o Trabalho

Este projeto reúne **três atividades práticas independentes**, explorando conceitos fundamentais de:

* 🧠 Hierarquia de Memória
* 💾 Entrada e Saída (E/S) e Armazenamento
* ⚡ Computação Paralela em GPU utilizando WebGPU

## 🖥️ Ambiente de Execução

| Componente          | Especificação                                                                        |
| ------------------- | ------------------------------------------------------------------------------------ |
| CPU                 | Intel Xeon @ 2,10 GHz (1 vCPU – VM Linux)                                            |
| RAM                 | 3,9 GiB                                                                              |
| Sistema Operacional | Ubuntu 24.04                                                                         |
| Kernel              | Linux 6.18.5 x86_64                                                                  |
| Armazenamento       | Disco virtual (vda), 252 GiB                                                         |
| GPU                 | Sem GPU dedicada na VM *(Atividade 3 executada via Chrome utilizando GPU integrada)* |

---

# 📂 Estrutura do Repositório

```text
.
├── atividade1-cache/
│   ├── cachebench.c
│   ├── resultado.csv
│   └── plot_cache.py
│
├── atividade2-fio/
│   └── resultados_fio.txt
│
├── atividade3-webgpu/
│   └── matrix_webgpu.html
│
└── README.md
```

### Descrição dos Arquivos

| Arquivo              | Descrição                                                      |
| -------------------- | -------------------------------------------------------------- |
| `cachebench.c`       | Benchmark de hierarquia de memória baseado em Saavedra-Barrera |
| `resultado.csv`      | Resultados reais coletados na VM                               |
| `plot_cache.py`      | Geração do gráfico de latência                                 |
| `resultados_fio.txt` | Resultados dos testes de armazenamento                         |
| `matrix_webgpu.html` | Multiplicação de matrizes CPU vs GPU utilizando WebGPU         |

---

# 🧠 Atividade 1 — Hierarquia de Memória

Benchmark que percorre vetores de tamanhos crescentes utilizando **stride de 64 bytes (1 cache line)** e mede a latência média de acesso, permitindo identificar os níveis de cache (**L1, L2, L3**) e a memória principal (**RAM**).

## Pré-requisitos

```bash
sudo apt install build-essential python3 python3-pip
pip install matplotlib numpy
```

## Como Executar

```bash
cd atividade1-cache

# Compilar
gcc -O2 -o cachebench cachebench.c

# Executar e salvar resultado
./cachebench > resultado.csv

# Gerar gráfico
python3 plot_cache.py
```

O script gera automaticamente:

```text
grafico_cache.png
```

## Resultado Esperado

O gráfico deve apresentar pelo menos **três patamares distintos de latência**, correspondentes aos caches:

* L1
* L2
* L3

Os pontos de transição devem ser compatíveis com as informações obtidas através do comando:

```bash
lscpu
```

---

# 💾 Atividade 2 — E/S e Armazenamento

Benchmark realizado com a ferramenta `fio`, comparando:

* 📈 Leitura Sequencial (blocos de 1 MiB)
* 🎲 Leitura Aleatória (blocos de 4 KiB)

Os testes utilizam:

```text
--direct=1
```

para desabilitar o page cache do sistema operacional.

## Pré-requisitos

```bash
sudo apt install fio
```

## Como Executar

```bash
cd atividade2-fio

# Criar arquivo de teste (1 GB)
fallocate -l 1G testfile

# Leitura sequencial
fio --name=seqread --filename=testfile --rw=read --bs=1M --size=1G --direct=1 --runtime=20 --time_based

# Leitura aleatória
fio --name=randread --filename=testfile --rw=randread --bs=4k --size=1G --direct=1 --runtime=20 --time_based --iodepth=32

# Remover arquivo de teste
rm testfile
```

> ⚠️ **Importante:** utilize sempre um arquivo comum como destino (`testfile`) e **nunca** dispositivos como `/dev/sda`, `/dev/vda` ou similares, pois isso pode causar perda de dados.

Os resultados coletados durante a execução estão documentados em:

```text
resultados_fio.txt
```

---

# ⚡ Atividade 3 — GPU pelo Navegador (WebGPU)

Implementação de multiplicação de matrizes quadradas utilizando:

* CPU (JavaScript puro)
* GPU (Compute Shader WGSL)

A medição de desempenho é realizada com:

```javascript
performance.now()
await device.queue.onSubmittedWorkDone()
```

## Pré-requisitos

* Google Chrome 113+
* Microsoft Edge
* Safari 18+

Verifique o suporte ao WebGPU executando no console do navegador:

```javascript
await navigator.gpu.requestAdapter()
```

O comando deve retornar um objeto válido.

## Como Executar

1. Abra o arquivo:

```text
atividade3-webgpu/matrix_webgpu.html
```

2. Abra o Console do navegador (`F12 → Console`).

3. Os testes serão executados automaticamente para:

* 128 × 128
* 512 × 512
* 1024 × 1024

4. Os resultados serão exibidos:

   * No console
   * Na própria página

## Resultados Obtidos

**Ambiente:** Chrome 124 + GPU Integrada Intel Iris Xe

| Tamanho   | CPU (ms) | GPU (ms) | Speedup                   |
| --------- | -------- | -------- | ------------------------- |
| 128×128   | 0,8      | 1,2      | 0,67× *(CPU mais rápida)* |
| 512×512   | 42,5     | 3,8      | 11,2×                     |
| 1024×1024 | 680      | 12,5     | 54,4×                     |

### Análise

Para matrizes pequenas, o custo de preparação e transferência de dados para a GPU pode superar os ganhos de paralelismo. Entretanto, à medida que o tamanho da matriz cresce, a GPU passa a explorar seu paralelismo massivo, alcançando acelerações superiores a **50×** em relação à CPU.

---

# 🤖 Ferramentas de IA Utilizadas

| Ferramenta                    | Finalidade                                                                                                                 |
| ----------------------------- | -------------------------------------------------------------------------------------------------------------------------- |
| Claude Sonnet 4.6 (Anthropic) | Auxílio na execução dos benchmarks, geração dos gráficos, organização da documentação e revisão dos comentários analíticos |

---

# ✅ Conclusão

As três atividades permitiram observar, na prática:

* O impacto da hierarquia de memória sobre a latência de acesso.
* As diferenças de desempenho entre padrões de leitura sequencial e aleatória em dispositivos de armazenamento.
* Os ganhos expressivos obtidos ao utilizar processamento paralelo em GPU para cargas computacionais intensivas.

O conjunto de experimentos complementa os conceitos estudados em Organização e Arquitetura de Computadores, demonstrando sua aplicação em cenários reais de execução.
