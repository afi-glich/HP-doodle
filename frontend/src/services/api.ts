import axios from "axios";

const API_BASE_URL =
process.env.REACT_APP_API_URL || "http://localhost:8000/api";

const api = axios.create({
baseURL: API_BASE_URL,
headers: {
"Content-Type": "application/json",
},
});

export interface HealthResponse {
status: string;
message: string;
}

export const checkHealth = async (): Promise<HealthResponse> => {
const response = await api.get<HealthResponse>("/health/");
return response.data;
};

export default api;