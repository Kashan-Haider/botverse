import React from 'react';
import Navbar from './pages/Navbar';

type LayoutProps = {
  children: React.ReactNode;
};

const Layout = ({ children }: LayoutProps) => {
  return (
    <div>
        <Navbar/>
      {children}
    </div>
  );
};

export default Layout;
