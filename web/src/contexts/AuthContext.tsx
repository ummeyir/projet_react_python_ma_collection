import {
	createContext,
	useContext,
	useEffect,
	useState,
	type PropsWithChildren,
} from "react";
import { ApiError, getCurrentUser, loginUser, registerUser } from "../services/apiClient";
import type { AuthUser, LoginRequest, RegisterRequest } from "../types/api";
import useLocalStorage from "../hooks/useLocalStorage";

interface AuthContextValue {
	token: string | null;
	user: AuthUser | null;
	isLoading: boolean;
	isAuthenticated: boolean;
	login: (payload: LoginRequest) => Promise<void>;
	register: (payload: RegisterRequest) => Promise<AuthUser>;
	logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

function AuthProvider({ children }: PropsWithChildren) {
	const [token, setToken] = useLocalStorage<string | null>("ma-collection-token", null);
	const [user, setUser] = useState<AuthUser | null>(null);
	const [isLoading, setIsLoading] = useState(true);

	useEffect(() => {
		const controller = new AbortController();
		if (!token) {
			setUser(null);
			setIsLoading(false);
			return () => controller.abort();
		}

		const accessToken = token;
		async function restoreSession(): Promise<void> {
			setIsLoading(true);
			try {
				setUser(await getCurrentUser(accessToken, controller.signal));
			} catch (error: unknown) {
				if (controller.signal.aborted) {
					return;
				}
				setUser(null);
				if (error instanceof ApiError && error.status === 401) {
					setToken(null);
				}
			} finally {
				if (!controller.signal.aborted) {
					setIsLoading(false);
				}
			}
		}

		void restoreSession();
		return () => controller.abort();
	}, [token, setToken]);

	async function login(payload: LoginRequest): Promise<void> {
		const response = await loginUser(payload);
		setToken(response.access_token);
		setUser(response.user);
	}

	async function register(payload: RegisterRequest): Promise<AuthUser> {
		return registerUser(payload);
	}

	function logout(): void {
		setToken(null);
		setUser(null);
	}

	return (
		<AuthContext.Provider
			value={{
				token,
				user,
				isLoading,
				isAuthenticated: token !== null && user !== null,
				login,
				register,
				logout,
			}}
		>
			{children}
		</AuthContext.Provider>
	);
}

function useAuth(): AuthContextValue {
	const context = useContext(AuthContext);
	if (context === null) {
		throw new Error("useAuth doit être utilisé dans AuthProvider");
	}
	return context;
}

export { AuthProvider, useAuth };
