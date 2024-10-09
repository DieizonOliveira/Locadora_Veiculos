import { PrismaClient } from "@prisma/client"
import { Router } from "express"

import { verificaToken } from "../middewares/verificaToken"

const prisma = new PrismaClient()

async function main() {
  /***********************************/
  /*     SOFT DELETE MIDDLEWARE      */
  /***********************************/
  prisma.$use(async (params, next) => {
    // Check incoming query type
    if (params.model == 'Carro') {
      if (params.action == 'delete') {
        // Delete queries
        // Change action to an update
        params.action = 'update'
        params.args['data'] = { deleted: true }
      }
    }
    return next(params)
  })
}
main()

const router = Router()

router.get("/", async (req, res) => {
  try {
    const carros = await prisma.carro.findMany({
      where: { deleted: false }
    })
    res.status(200).json(carros)
  } catch (error) {
    res.status(400).json(error)
  }
})

router.get("/:id", async (req, res) => {
  const { id } = req.params;
  try {
    const carro = await prisma.carro.findUnique({
      where: { id: Number(id), deleted: false }
    });
    if (!carro) {
      res.status(404).json({ erro: `Veículo com o ID ${id} não encontrado` });
      return;
    }
    res.status(200).json(carro);
  } catch (error) {
    res.status(400).json(error);
  }
});

router.get("/contagem/marcas", async (req, res) => {
  try {
    const contagemPorMarca = await prisma.carro.groupBy({
      by: ['marca'],
      _count: {
        marca: true,
      },
      where: { deleted: false },
    })
    res.status(200).json(contagemPorMarca)
  } catch (error) {
    res.status(400).json(error)
  }
})


// Rota para obter modelos e custo mensal de todos os carros
router.get('/carros/modelo-custo', async (req, res) => {
  try {
    const carros = await prisma.carro.findMany({
      select: {
        modelo: true,
        custo_mensal: true,
      },
      where: {
        deleted: false, // Considerando que você tem soft delete implementado
      },
    });
    res.status(200).json(carros);
  } catch (error) {
    res.status(500).json({ error: 'Erro ao buscar os carros.' });
  }
});

router.post("/", verificaToken, async (req: any, res) => {
  // dados que são fornecidos no corpo da requisição
  const { modelo, marca, ano, custo_mensal, QtdPassageiros } = req.body

  // dado que é acrescentado pelo Token (verificaToken) no req
  const { userLogadoId } = req

  if (!modelo || !marca || !ano || !custo_mensal || !QtdPassageiros) {
    res.status(400).json({ erro: "Informe modelo, marca, ano, custo mensal e nº de passageiros do automóvel!" })
    return
  }

  try {
    const carro = await prisma.carro.create({
      data: { modelo, marca, ano, custo_mensal, QtdPassageiros, usuarioId: userLogadoId }
    })
    res.status(201).json(carro)
  } catch (error) {
    res.status(400).json(error)
  }
})

router.delete("/:id", verificaToken, async (req, res) => {
  const { id } = req.params

  try {
    const carro = await prisma.carro.delete({
      where: { id: Number(id) }
    })
    res.status(200).json(carro)
  } catch (error) {
    res.status(400).json(error)
  }
})

router.put("/:id", verificaToken, async (req, res) => {
  const { id } = req.params;
  const { modelo, marca, ano, custo_mensal, QtdPassageiros } = req.body;

  if (!modelo || !marca || !ano || !custo_mensal || !QtdPassageiros) {
    res.status(400).json({ erro: "Informe modelo, marca, ano, custon mensal e nº de passageiros do automóvel!" });
    return;
  }

  try {
    // Busca o carro atual no banco de dados antes de atualizar
    const carroAtual = await prisma.carro.findUnique({
      where: { id: Number(id) },
    });

    if (!carroAtual) {
      res.status(404).json({ erro: "Veículo não encontrado" });
      return;
    }

    // Realiza a atualização no banco de dados
    const carroAtualizado = await prisma.carro.update({
      where: { id: Number(id) },
      data: { modelo, marca, ano, custo_mensal, QtdPassageiros },
    });

    res.status(200).json(carroAtualizado);
  } catch (error) {
    res.status(400).json(error);
  }
});

export default router