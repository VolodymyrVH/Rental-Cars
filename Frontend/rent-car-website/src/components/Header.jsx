import logo from '../assets/logoheader.png'
import React from 'react'
import './Style.css'

function Header() {
    return (
        <header>
            <div className="header_outline">
                <div className="logoside"><img src={logo} alt="Logo" /></div>
                <div className="menusude">
                    <ul className="header-navigation">
                        <li><a href="#">EUR</a></li>
                        <li><a href="#">English</a></li>
                        <li><a href="#">Help</a></li>
                        <li><a href="#">Manage booking</a></li>
                        <li><a href="#">Sign in</a></li>
                    </ul>
                </div>
            </div>
        </header>
    )

}

export default Header