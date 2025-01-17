# LAPS para Linux

O objetivo desse script é a alteração de senha do usuário root no Linux de forma aleatória e armazenamento dessa senha no Active Directory, assim como é feito com o Windows.\
A conexão e alteração da senha é feita via protocolo LDAPS.\
O atributo de computador que armazena a senha chama-se msLAPS-Password.

No momento a senha não é criptografada como é feito no Windows.\
No momento a opção de visualização de senha é somente via Aba "Editor de Atributos" ou via "Powershell".\

## Configuração

É necessário ter um usuário com permissões de alteração na OU que contenha os servidores Linux, no atributo:
- msLAPS-Password

Configure as variáveis de ambiente:
- SERVIDOR_LDAP
- USUARIO_LDAP
- SENHA_LDAP
- BASE_DN

Altere a permissão do arquivo para que somente o root tenha permissões:
```
chmod 700 /opt/laps.py
```

## Execução direta Servidor

Crie uma tarefa agendada (crontab) para ser executada uma vez a cada 30 dias apontando para o script.\
Exemplo:
```
 00 10 1 * * python3 /opt/laps.py
```

## Playbook Ansible

```
ansible-playbook -i $INVENTORY $PLAYBOOK.yaml -u $usuariolinux --limit=$HOSTS --extra-vars "server=$LDAP_SERVER" --extra-vars "user=$LDAP_USER" --extra-vars "pass=$LDAP_PASS" --extra-vars "base=$BASE_DN" -b
```

## Consulta da senha

Somente "Admins do Domínio" conseguirão consultar a senha, conforme é feito com os Servidores Windows.
```
Get-ADComputer SERVIDOR101 -Properties mslaps-password
```


