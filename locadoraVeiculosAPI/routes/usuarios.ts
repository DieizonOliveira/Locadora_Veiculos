import { PrismaClient } from "@prisma/client";
import { Router } from "express";
import bcrypt from 'bcrypt';

const prisma = new PrismaClient();
const router = Router();

function validaSenha(senha: string) {
  const mensa: string[] = [];

  if (senha.length < 8) {
    mensa.push("Erro... senha deve possuir, no mínimo, 8 caracteres");
  }

  let pequenas = 0;
  let grandes = 0;
  let numeros = 0;
  let simbolos = 0;

  for (const letra of senha) {
    if ((/[a-z]/).test(letra)) {
      pequenas++;
    } else if ((/[A-Z]/).test(letra)) {
      grandes++;
    } else if ((/[0-9]/).test(letra)) {
      numeros++;
    } else {
      simbolos++;
    }
  }

  if (pequenas === 0 || grandes === 0 || numeros === 0 || simbolos === 0) {
    mensa.push("Erro... senha deve possuir letras minúsculas, maiúsculas, números e símbolos");
  }

  return mensa;
}

router.get("/", async (req, res) => {
  try {
    const usuarios = await prisma.usuario.findMany();
    res.status(200).json(usuarios);
  } catch (error) {
    res.status(400).json(error);
  }
});

// Rota para atualização de senha
router.put("/senha", async (req, res) => {
  const { id, senhaAtual, novaSenha } = req.body;

  if (!id || !senhaAtual || !novaSenha) {
    res.status(400).json({ erro: "Informe o ID do usuário, senha atual e nova senha" });
    return;
  }

  try {
    const usuario = await prisma.usuario.findUnique({
      where: { id: Number(id) },
    });

    if (!usuario) {
      res.status(404).json({ erro: "Usuário não encontrado" });
      return;
    }

    if (!bcrypt.compareSync(senhaAtual, usuario.senha)) {
      res.status(400).json({ erro: "Senha atual incorreta" });
      return;
    }

    const errosNovaSenha = validaSenha(novaSenha);
    if (errosNovaSenha.length > 0) {
      res.status(400).json({ erro: errosNovaSenha.join("; ") });
      return;
    }

    const salt = bcrypt.genSaltSync(12);
    const hashNovaSenha = bcrypt.hashSync(novaSenha, salt);

    const usuarioAtualizado = await prisma.usuario.update({
      where: { id: Number(id) },
      data: { senha: hashNovaSenha },
    });

    res.status(200).json(usuarioAtualizado);
  } catch (error) {
    res.status(400).json(error);
  }
});

// Rota para criação de usuário
router.post("/", async (req, res) => {
  const { nome, email, senha } = req.body;

  if (!nome || !email || !senha) {
    res.status(400).json({ erro: "Informe nome, email e senha" });
    return;
  }

  const errosSenha = validaSenha(senha);
  if (errosSenha.length > 0) {
    res.status(400).json({ erro: errosSenha.join("; ") });
    return;
  }

  try {
    // Verifica se o e-mail já está em uso
    const existingUser = await prisma.usuario.findFirst({
      where: { email },
    });

    if (existingUser) {
      res.status(400).json({ erro: "E-mail já está em uso. Escolha outro e-mail." });
      return;
    }

    const salt = bcrypt.genSaltSync(12);
    const hash = bcrypt.hashSync(senha, salt);

    const usuario = await prisma.usuario.create({
      data: { nome, email, senha: hash },
    });
    res.status(201).json(usuario);
  } catch (error) {
    res.status(400).json(error);
  }
});

export default router;
