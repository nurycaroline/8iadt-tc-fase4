// Carregamento de segredos do Azure Key Vault (Fase 7 — F7-07 / docs/07 §2).
//
// Quando AZURE_KEY_VAULT_URL está definido, busca os segredos no cofre e os injeta em process.env
// (sem sobrescrever valores já presentes). Caso contrário — ou se o SDK/cofre estiver indisponível —
// cai no fallback `.env`/variáveis de ambiente atuais (docs/07 §2: "Key Vault **ou** .env").
//
// IMPORTANTE: este módulo NÃO importa `config`/`logger` (que leem env no import); ele deve rodar
// ANTES de `config` ser avaliado (ver src/bootstrap.js) para que os valores do cofre tenham efeito.

// Segredos suportados → nome no Key Vault (env var com `_` vira `-`, convenção do Key Vault).
const SEGREDOS = ['API_KEY', 'AI_SERVICE_API_KEY', 'AZURE_STORAGE_CONNECTION_STRING'];

export async function carregarSegredos({ env = process.env } = {}) {
  const url = env.AZURE_KEY_VAULT_URL;
  if (!url) return { fonte: 'env', carregados: [] };

  let SecretClient;
  let DefaultAzureCredential;
  try {
    ({ SecretClient } = await import('@azure/keyvault-secrets'));
    ({ DefaultAzureCredential } = await import('@azure/identity'));
  } catch (err) {
    console.warn(`[segredos] SDK do Key Vault indisponível; usando .env (${String(err)})`);
    return { fonte: 'env', carregados: [] };
  }

  try {
    const client = new SecretClient(url, new DefaultAzureCredential());
    const carregados = [];
    for (const nome of SEGREDOS) {
      if (env[nome]) continue; // env/.env tem precedência sobre o cofre.
      try {
        const segredo = await client.getSecret(nome.replace(/_/g, '-'));
        if (segredo?.value) {
          env[nome] = segredo.value;
          carregados.push(nome);
        }
      } catch {
        // Segredo ausente no cofre: mantém o fallback .env (não falha por segredo opcional).
      }
    }
    console.info(`[segredos] carregados do Key Vault: ${carregados.join(', ') || '(nenhum)'}`);
    return { fonte: 'keyvault', carregados };
  } catch (err) {
    console.error(`[segredos] falha ao acessar o Key Vault; usando .env (${String(err)})`);
    return { fonte: 'env', carregados: [] };
  }
}
