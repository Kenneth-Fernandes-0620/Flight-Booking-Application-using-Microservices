import { GridOutline } from "react-ionicons";
import logo from '../../../public/logo.png';

const Navbar = () => {
	const url = 'http://localhost:5173/'
	const navLinks = [
		{ title: "Why us?", path: `${url}#features`, active: false },
		{ title: "Services", path: `${url}#services`, active: false },
		{ title: "Blog", path: `${url}#blog`, active: false },
		{ title: "Contact", path: `${url}#contact`, active: false },
		{ title: "About", path: `${url}#about`, active: false },
	];
	return (
		<div className="z-[2] w-full my-auto mx-0 h-16 md:px-[200px] px-8 py-10 flex items-center justify-between absolute top-[20px]">
			<span className="font-semibold">
				<img src={logo} alt="logo" className="w-50 h-10" />
			</span>
			<div className="md:flex hidden items-center gap-7">
				{navLinks.map((navLink) => {
					return (
						<a href={navLink.path} key={navLink.title}>
							<span
								className={`font-medium ${navLink.active ? "text-blue-400" : "text-white"}`}
							>
								{navLink.title}
							</span>
						</a>
					);
				})}
				<a href="/booking" className="bg-blue-400 rounded-full text-gray-900 px-6 py-3 font-semibold hover:bg-gray-700 hover:text-white">
					Book Now
				</a>
			</div>
			<div className="cursor-pointer md:hidden block">
				<GridOutline color="#fff" />
			</div>
		</div>
	);
};

export default Navbar;
