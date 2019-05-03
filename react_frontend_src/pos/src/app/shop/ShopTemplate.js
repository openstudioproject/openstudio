import React from "react"
  
// add protypes

// import PosMenu from "./PosMenu"
// import Content from "./ui/Content";
// import ErrorScreen from "./ui/ErrorScreen";

import PageTemplate from '../../components/PageTemplate'
import ShopMainMenu from "./MainMenu";
import Cart from "./cart/CartContainer"
import CartTools from "./cart/CartToolsContainer"

const ShopTemplate = ({ app_state, children }) =>
    <PageTemplate app_state={app_state}>
        <div className="row shop-content-row">
            <div className="col-md-4 shop-cart">
            <Cart />
            <CartTools />
            </div>
            <div className="col-md-8 shop-products">
            <ShopMainMenu>
                <div className="shop-products-content">
                    {children}
                </div>
            </ShopMainMenu>
            </div>
        </div>
    </PageTemplate>

export default ShopTemplate

