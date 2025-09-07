class TextSystem:
    def __init__(self):
        self.textos = {
            "basic": (
                "`ping` - Mostra a latência do bot\n"
                "`rep @user` - Dá reputação para um usuário\n"
                "`help` - Mostra esta mensagem de ajuda\n"
                "`avatar @user`(opcional) - Exibe o avatar de um usuário\n"
                "`status` - Exibe os status no servidor\n"
                "`xp` - Exibe o xp do usuário no servidor\n"
            ),
            "admin": (
                "`addchannel #channel` ou `id` - Adiciona um canal ao sistema\n"
                "`removechannel #channel` ou `id` - Remove um canal do sistema\n"
                "`channel` - Mostra os canais configurados\n"
                "`update @user type amount` - Adiciona recursos a um usuário\n"
                "`updateremove @user type amount` - Remove recursos de um usuário\n"
                "`addmoney @user amount` - Adiciona dinheiro a um usuário\n"
                "`addxp @user amount` - Adiciona XP a um usuário\n"
                "`addlevel @user amount` - Adiciona níveis a um usuário\n"
                "`addvoice @user amount` - Adiciona tempo de voz a um usuário\n"
                "`addmessage @user amount` - Adiciona mensagens a um usuário\n"
                "`addrole @user @role` - Adiciona um cargo a um usuário\n"
                "*(Todos os comandos add têm versão remove)*\n"
                "**Tipos (type):** `xp`, `level`, `voice`, `message`, `money`, `rep`\n"
            ),
            "profile": (
                "`perfil @user`(opcional) - Mostra o perfil completo de um usuário\n"
                "`rank @user`(opcional) - Mostra o rank de um usuário\n"
                "`stats @user`(opcional) - Mostra as estatísticas de um usuário\n"
                "`top type`(opcional) - Mostra o top de usuários por tipo\n"
                "**Tipos disponíveis para top:** `money`, `rep`\n"
            ),
            "house": (
                "`htk` - Cria o ticket para testes das casas\n"
                "`casas` - Mostra informações das casas em gerais\n"
            ),
            "economy": (
                "`carteira` - Exibe o saldo em bkz do usuário\n"
                "`pagar` - Faz um pagamento a um usuário\n"
            )
        }
        self.text_levels = {
            "5": "Você deixou de ser um zero... para se tornar um um. Não chore ainda — o abismo está só começando a sorrir para você.",
            "10": "Você é como uma vela na tempestade: insignificante, mas... quase digno de pena. Continue assim e talvez eu não o apague.",
            "15": "Você evoluiu de patético para tolerável. Uma conquista... se ignorarmos o quão baixo era o padrão.",
            "20": "Parabéns: você é agora uma ratazana em um labirinto de titânio. Continue roendo... talvez encontre migalhas de minha atenção.",
            "25": "Você se tornou uma ferramenta... afiada o suficiente para ser útil, mas ainda descartável. Use-se bem.",
            "30": "Você brilha como um fogo-fátuo no pântano. Engana tolos... mas eu não sou tão fácil de iludir.",
            "40": "Você é um peão em meu tabuleiro. Não se iluda: até peões têm momentos gloriosos... antes de serem sacrificados.",
            "50": "Você está no coração do labirinto. As paredes sussurram seu nome... e eu adoro finais trágicos.",
            "65": "Você arrancou um sussurro de interesse de mim. Mas cuidado: até sussurros podem estrangular.",
            "70": "Você entrou em meu campo de visão. Agora... dance. Eu adoro um espetáculo antes da queda.",
            "85": "Você está na beirada do abismo. Pule. Eu prometo rir com elegância.",
            "100": "Você alcançou o topo. Mas lembre-se: coroas são pesadas... e eu adoro ver joias quebradas aos meus pés."
          }
            
        