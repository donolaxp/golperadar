def calcular_risco(dados):
    risco = 0
    
    if not dados['ssl_valido']:
        risco += 40
    
    # Só penaliza se a gente CONSEGUIU ver a idade
    if dados['idade_dias'] is not None:
        if dados['idade_dias'] < 7:
            risco += 30
        elif dados['idade_dias'] < 30:
            risco += 15
    
    if dados['redireciona']:
        risco += 20
    
    if risco >= 70:
        status = 'GOLPE PROVÁVEL'
    elif risco >= 40:
        status = 'SUSPEITO'
    else:
        status = 'SEGURO'
    
    return min(risco, 100), status