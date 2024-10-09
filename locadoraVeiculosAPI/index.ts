import express from 'express'
const app = express()
const port = 3000
import cors from 'cors'

import CarrosRoutes from './routes/carros'
import usuariosRoutes from './routes/usuarios'
import loginRoutes from './routes/login'

app.use(express.json())
app.use(cors())
app.use("/carros", CarrosRoutes)
app.use("/usuarios", usuariosRoutes)
app.use("/login", loginRoutes)

app.get('/', (req, res) => {
  res.send('API da Locadora: Controle de Veículos')
})

app.listen(port, () => {
  console.log(`Servidor rodando na porta: ${port}`)
})