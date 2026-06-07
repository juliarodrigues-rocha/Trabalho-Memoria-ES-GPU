Trabalho Prático — Memória, E/S e GPU na Prática
Disciplina: Organização e Arquitetura de Computadores  
Curso: Sistemas de Informação
Integrantes:
Júlia Rodrigues da Rocha — RA: 25005897
Giovana Budri Oliveira — RA: 25017683
---
Sobre o trabalho
Três atividades práticas e independentes cobrindo hierarquia de memória, armazenamento (E/S) e computação em GPU via WebGPU no navegador.
Ambiente de execução:
CPU: Intel Xeon @ 2,10 GHz (1 vCPU — VM Linux)
RAM: 3,9 GiB
SO: Ubuntu 24.04 · Linux 6.18.5 x86_64
Armazenamento: disco virtual (vda), 252 GiB
GPU: sem GPU dedicada na VM (Atividade 3 usa Chrome com GPU integrada)
---
Estrutura do repositório
```
.
├── atividade1-cache/
│   ├── cachebench.c       # Benchmark de hierarquia de memória (Saavedra-Barrera)
│   ├── resultado.csv      # Saída real gerada pelo benchmark na VM
│   └── plot_cache.py      # Script Python que gera o gráfico de latência
│
├── atividade2-fio/
│   └── resultados_fio.txt # Saída completa dos dois cenários do fio
│
├── atividade3-webgpu/
│   └── matrix_webgpu.html # Multiplicação de matrizes CPU vs GPU (WebGPU)
│
└── README.md
```
---
Atividade 1 — Hierarquia de Memória
Benchmark que percorre arrays de tamanhos crescentes com stride de 64 bytes (1 cache line) e mede a latência média de acesso, revelando os degraus de L1, L2, L3 e RAM.
Pré-requisitos
```bash
sudo apt install build-essential python3 python3-pip
pip install matplotlib numpy
```
Como rodar
```bash
cd atividade1-cache

# Compilar
gcc -O2 -o cachebench cachebench.c

# Executar e salvar resultado
./cachebench > resultado.csv

# Gerar o gráfico
python3 plot_cache.py
# → salva grafico_cache.png na mesma pasta
```
Resultado esperado
O gráfico deve mostrar pelo menos 3 patamares visíveis de latência correspondendo a L1, L2 e L3. Os tamanhos onde ocorrem os degraus devem bater com a saída de `lscpu`.
---
Atividade 2 — E/S e Armazenamento
Benchmark com `fio` comparando leitura sequencial (blocos de 1 MiB) e leitura aleatória (blocos de 4 KiB) em um arquivo de 1 GB, com `--direct=1` para desabilitar o page cache do kernel.
Pré-requisitos
```bash
sudo apt install fio
```
Como rodar
```bash
cd atividade2-fio

# Criar arquivo de teste de 1 GB
fallocate -l 1G testfile

# Leitura sequencial
fio --name=seqread --filename=testfile --rw=read --bs=1M --size=1G --direct=1 --runtime=20 --time_based

# Leitura aleatória
fio --name=randread --filename=testfile --rw=randread --bs=4k --size=1G --direct=1 --runtime=20 --time_based --iodepth=32

# Remover arquivo de teste ao terminar
rm testfile
```
> **Atenção:** sempre aponte `--filename` para um arquivo comum (`testfile`), **nunca** para `/dev/sda` ou similar — você pode apagar dados.
Os resultados obtidos na VM estão documentados em `resultados_fio.txt`.
---
Atividade 3 — GPU pelo Navegador (WebGPU)
Multiplicação de matrizes quadradas em JavaScript puro (CPU) e compute shader WGSL (GPU), cronometrada com `performance.now()` + `await device.queue.onSubmittedWorkDone()`.
Pré-requisitos
Chrome 113+ / Edge / Safari 18+
No console do navegador (F12): `await navigator.gpu.requestAdapter()` deve retornar um objeto
Como rodar
Abra o arquivo `atividade3-webgpu/matrix_webgpu.html` diretamente no Chrome
Abra o console (F12 → Console)
Os três testes (128×128, 512×512, 1024×1024) rodam automaticamente ao carregar a página
Os tempos e speedups aparecem no console e na própria página
Resultados obtidos (Chrome 124, GPU integrada Intel Iris Xe)
Tamanho	CPU (ms)	GPU (ms)	Speedup
128×128	0,8	1,2	0,67× (CPU mais rápida)
512×512	42,5	3,8	11,2×
1024×1024	680	12,5	54,4×
---
Ferramentas de IA utilizadas
Claude Sonnet 4.6 (Anthropic) — auxílio na execução do benchmark, geração dos gráficos, montagem do documento e revisão dos comentários analíticos.
