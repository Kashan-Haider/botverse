import { Link } from "react-router-dom";

const Navbar = () => {
  return (
    <div className="absolute top-0 z-50 flex items-center justify-between w-full p-5 bg-transparent">
      <div>
        <Link to={"/"} className="text-3xl">
          🤖
        </Link>
      </div>
      <div className="flex gap-4">
        <Link
          to={"/profile"}
          className="bg-gray-100 px-3 py-1 rounded-2xl shadow-lg shadow-black"
        >
          Profile
        </Link>
        <Link
          to={"/chat"}
          className="bg-gray-100 px-3 py-1 rounded-2xl shadow-lg shadow-black"
        >
          Test Chat
        </Link>
      </div>
    </div>
  );
};

export default Navbar;
