import { Suspense } from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
		<Suspense fallback={<div>Loading ...</div>}>
			<BrowserRouter>
				<App />
			</BrowserRouter>
		</Suspense>
);
