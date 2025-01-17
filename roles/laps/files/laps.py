#!/usr/bin/env python3

"""
O objetivo desse script é a alteração de senha do usuário root no Linux de forma aleatória e armazenamento dessa senha no Active Directory, assim como é feito com o Windows.
A conexão e alteração da senha é feita via protocolo LDAPS.
O atributo de computador que armazena a senha chama-se msLAPS-Password.

Configuração:
É necessário ter um usuário com permissões de alteração na OU que contenha os servidores Linux, no atributo:
- msLAPS-Password

Configure as variáveis:
- SERVIDOR_LDAP
- USUARIO_LDAP
- SENHA_LDAP
- BASE_DN
"""

__version__ = "0.0.2"
__author__ = "Juliano Ribeiro"
__license__ = "Unlicense"


import random
import string
import socket
import subprocess
import sys
import os
import time
from ldap3 import Server, Connection, ALL, MODIFY_REPLACE, SUBTREE


SERVIDOR_LDAP = os.getenv("SERVIDOR_LDAP")
USUARIO_LDAP = os.getenv("USUARIO_LDAP")
SENHA_LDAP = os.getenv("SENHA_LDAP")
BASE_DN = os.getenv("BASE_DN")


# Função para gerar uma senha aleatória de 12 caracteres
def gerar_senha():
    caracteres = string.ascii_letters + string.digits + "!@#$%&*_-"
    senha = ''.join(random.choice(caracteres) for i in range(12))
    return senha

# Função para obter o DN do computador no LDAP baseado no hostname
def obter_dn_computador(conn, hostname):
    search_filter = f"(CN={hostname})"
    conn.search(BASE_DN, search_filter, search_scope=SUBTREE, attributes=['distinguishedName'])

    if conn.entries:
        return conn.entries[0].distinguishedName
    raise ValueError(f"Computador com hostname {hostname} não encontrado no LDAP.")


# Função para conectar ao servidor LDAP
def conectar_ldap():
    try:
        server = Server(SERVIDOR_LDAP, get_info=ALL)
        conn = Connection(server, user=USUARIO_LDAP, password=SENHA_LDAP, auto_bind=True)
        print("Conexão LDAP bem-sucedida!")
        return conn
    except Exception as e:
        print(f"Erro ao conectar no servidor LDAP: {e}")
        sys.exit(1)

# Função para alterar a senha no Active Directory
def alterar_senha_ad(conn, campo_computador, nova_senha_msLAPS):
    try:
        # Modificar o atributo 'msLAPS-Password'
        conn.modify(campo_computador, {'msLAPS-Password': [(MODIFY_REPLACE, [nova_senha_msLAPS])]})

        # Verificar se a modificação foi bem-sucedida
        if conn.result['result'] == 0:
            print(f"A senha msLAPS-Password do computador {campo_computador} foi alterada com sucesso!")
        else:
            print(f"Erro ao alterar a senha no AD: {conn.result['description']}")
    except Exception as e:
        print(f"Erro ao alterar o atributo no AD: {e}")
        sys.exit(1)


# Função para alterar a senha do usuario no Linux
def alterar_senha_linux(user,nova_senha_msLAPS):
    comando = f"echo '{user}:{nova_senha_msLAPS}' | sudo chpasswd"
    try:
        processo = subprocess.run(comando, shell=True, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"A senha do {user} no Linux foi alterada com sucesso.")
    except subprocess.CalledProcessError as e:
        print(f"Erro ao alterar a senha do {user} no Linux: {e.stderr.decode('utf-8')}")
        sys.exit(1)


# Função principal
def main():
    hostname = socket.gethostname()
    nova_senha_msLAPS = gerar_senha()

    # Conectar ao LDAP
    conn = conectar_ldap()

    # Obter o DN do computador via LDAP
    campo_computador = str(obter_dn_computador(conn, hostname))
    print(f"Distinguished Name do computador {hostname}: {campo_computador}")

    # Alterar a senha no Active Directory
    alterar_senha_ad(conn, campo_computador, nova_senha_msLAPS)

    # Alterar a senha do root no Linux
    user = "root"
    alterar_senha_linux(user,nova_senha_msLAPS)

    # Fechar a conexão LDAP
    conn.unbind()


# Executar o script
if __name__ == "__main__":
    main()