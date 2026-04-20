"""
__main__.py — Ponto de entrada do Servidor.
"""

from server.Server import Server

def main():
    print("[SISTEMA] Inicializando o Servidor...")
    
    try:
        server = Server()
        server.run()
        
    except KeyboardInterrupt:
        print("\n[SISTEMA] Servidor encerrado pelo utilizador (Ctrl+C).")

    except Exception as e:
        print(f"[ERRO CRÍTICO] Falha ao iniciar o servidor: {e}")

if __name__ == "__main__":
    main()