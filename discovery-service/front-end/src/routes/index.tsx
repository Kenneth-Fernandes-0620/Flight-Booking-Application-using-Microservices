import { RouteObject } from "react-router";
import Home from "../pages/Home";
import Layout from "../layout";
import Booking from "../pages/Booking";

const routes: RouteObject[] = [
	{
		path: "/",
		element: <Layout />,
		children: [
			{
				children: [
					{
						path: "",
						element: <Home />,
					},
					{
						path: "booking",
						element: <Booking />,
					}
				],
			},
		],
	},
];

export default routes;
