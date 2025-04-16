class TextSystem:
	def __init__(self):
		self.textos = {
			"adm": (
				"addxp @user amount - Adiciona xp a um membro.\n"
        		"addlevel @user amount - Adiciona levels a um membro.\n"
        		"removexp @user amount - Remove xp de um membro.\n"
        		"removelevel @user amount - Remove levels de um membro.\n"
			),
			"basic": (
				"rank @user - Exibe seu rank ou de um membro.\n"
	            "diga <mensagem> - O bot repete a mensagem.\n"
	            "ask <pergunta> - Faz uma pergunta a Bei Bei.\n"
	            "perfil - Exibe seu perfil.\n"
	            "top - Mostra o ranking dos usuários.\n"
	            "avatar - Exibe seu avatar."
			)
		}
