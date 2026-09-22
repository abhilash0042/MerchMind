// src/app/services/api.ts

const isDev = import.meta.env.DEV;
const API_BASE_URL = isDev ? "/api" : (import.meta.env.VITE_API_URL || "/api");
const AI_API_BASE_URL = isDev ? "/ai-api" : (import.meta.env.VITE_AI_API_URL || "/ai-api");
const API_KEY = import.meta.env.VITE_API_KEY || 'dev-api-key';

// Seller info — will be set dynamically after creating/fetching the seller
let _sellerId: string | null = null;

export function getSellerId(): string | null {
  return _sellerId;
}

export function setSellerId(id: string) {
  _sellerId = id;
}

export const apiClient = {
  async get(endpoint: string) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    };
    if (_sellerId) {
      headers['X-Seller-Id'] = _sellerId;
    }
    const response = await fetch(url, { method: 'GET', headers });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`GET ${endpoint} failed (${response.status}): ${body}`);
    }
    return response.json();
  },

  async post(endpoint: string, data: Record<string, unknown>, sellerId?: string) {
    const sid = sellerId || _sellerId;
    let path = endpoint;
    if (sid && !/[?&]seller_id=/.test(path)) {
      path += path.includes('?') ? '&' : '?';
      path += `seller_id=${encodeURIComponent(sid)}`;
    }
    const url = `${API_BASE_URL}${path}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      'X-API-Key': API_KEY,
    };
    if (sid) {
      headers['X-Seller-Id'] = sid;
    }
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`POST ${endpoint} failed (${response.status}): ${body}`);
    }
    return response.json();
  },

  async postForm(endpoint: string, formData: FormData) {
    const url = `${API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'X-API-Key': API_KEY,
    };
    if (_sellerId) {
      headers['X-Seller-Id'] = _sellerId;
    }
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: formData,
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`POST ${endpoint} failed (${response.status}): ${body}`);
    }
    return response.json();
  },
};

export const aiApiClient = {
  async post(endpoint: string, data: Record<string, unknown>) {
    const url = `${AI_API_BASE_URL}${endpoint}`;
    const headers: Record<string, string> = {
      'Content-Type': 'application/json',
      // AI API does not strictly require API key at this exact moment according to main.py, but safe to include if they add it
    };
    const response = await fetch(url, {
      method: 'POST',
      headers,
      body: JSON.stringify(data),
    });
    if (!response.ok) {
      const body = await response.text();
      throw new Error(`AI POST ${endpoint} failed (${response.status}): ${body}`);
    }
    return response.json();
  },
};

let _sellerPromise: Promise<string> | null = null;

/**
 * Ensures a seller exists in the backend. Creates one if none exist.
 * Returns the seller_id to use for all subsequent API calls.
 */
export async function ensureSeller(): Promise<string> {
  if (_sellerId) return _sellerId;
  if (_sellerPromise) return _sellerPromise;

  _sellerPromise = (async () => {
    try {
      const sellers = await apiClient.get('/sellers/');
      // Find our specific startup seller
      const brewBoulevard = sellers.find((s: any) => s.seller_name === 'Brew Boulevard');
      if (brewBoulevard) {
        _sellerId = brewBoulevard.seller_id;
        return _sellerId!;
      }
    } catch (err) {
      console.warn("Sellers check failed, will attempt to create:", err);
    }

    // Create the one and only Brew Boulevard identity
    try {
      const newSeller = await apiClient.post('/sellers/', {
        seller_name: 'Brew Boulevard',
        marketplace: 'multi',
        region: 'IN',
        email: 'hello@brewboulevard.in',
      });
      _sellerId = newSeller.seller_id;
      return _sellerId!;
    } catch (err) {
      console.error("Failed to initialize Brew Boulevard:", err);
      _sellerPromise = null; // allow retry on next call
      throw err;
    }
  })();

  return _sellerPromise;
}

// -------------------------------------------------------------------
// AI Product Intelligence API Calls
// -------------------------------------------------------------------

export async function fetchProductsWithAnalysis(sellerId: string) {
  return await apiClient.get(`/analytics/products/list?seller_id=${sellerId}`);
}

export async function triggerProductAnalysis(sellerId: string, productId: string) {
  // Uses POST so we use the post method but with query params since FastAPI endpoint takes them as params
  return await apiClient.post(`/ai/analyze/product?seller_id=${sellerId}&product_id=${productId}`, {});
}

export async function getProductAnalysis(sellerId: string, productId: string) {
  return await apiClient.get(`/ai/analysis/${productId}?seller_id=${sellerId}`);
}

export async function getProductMetrics(sellerId: string, productId: string) {
  return await apiClient.get(`/analytics/product/${productId}/metrics?seller_id=${sellerId}`);
}

export async function getProductPayments(sellerId: string, productId: string) {
  return await apiClient.get(`/payments/product/${productId}?seller_id=${sellerId}`);
}

export async function getPaymentsAnalysis(sellerId: string) {
  return await apiClient.get(`/payments/analysis?seller_id=${sellerId}`);
}

export async function askPaymentsQuestion(sellerId: string, question: string, runId?: string) {
  return await apiClient.post('/payments/ask', { seller_id: sellerId, question, run_id: runId || null }, sellerId);
}
