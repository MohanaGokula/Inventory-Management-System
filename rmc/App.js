import React from 'react';
import './App.css';
import { BrowserRouter, Redirect, Route,Link,NavLink, Routes, Navigate,
  Outlet} from 'react-router-dom';
  import { useNavigate } from 'react-router';
import {  useState, useEffect } from 'react';
import Home from "./Home";

import Login from "./Login";
import { CookiesProvider } from 'react-cookie';

import PurchaseOrder from "./forms/purchase/PurchaseOrder";
import { useCookies } from 'react-cookie';
import PurchaseOrderTable from './forms/purchase/PurchaseOrderTable';
import PurchaseOrderEdit from './forms/purchase/PurchaseOrderEdit';
import MaterialReceiptNote from './forms/store/MaterialReceiptNote';
import GoodsReceiptNote from './forms/store/GoodsReceiptNote';
import QuotationTable from './forms/marketing/QuotationTable';


function App() {
    const [category, setCategory,removeCategory] = useCookies(['myCategory']);
    const [superuser,setSuperuser,removeSuperuser] = useCookies(['mySuperuser']);
    
    
    // const PurchaseWrapper = () => {
    //   return ((superuser['mySuperuser']) || (category['myCategory'].includes("is_purchase") === true)) ? <Outlet /> : <Navigate to="/Home" />;
    // };
  
  return (
    // <>
<CookiesProvider>
    <BrowserRouter>
            <Routes>
                <Route exact path="/" element={<Login />} />
                <Route exact path="/Home" element={<Home />} />
                <Route path="/PurchaseOrder" element={<PurchaseOrder/>} />
                <Route path="/PurchaseOrderTable" element={<PurchaseOrderTable/>} />
                <Route path="/PurchaseOrderEdit/:id" element={<PurchaseOrderEdit/>} />
                <Route path="/MaterialReceiptNote" element={<MaterialReceiptNote/>} />
                <Route path="/GoodsReceiptNote" element={<GoodsReceiptNote/>} />

                
                
                {/* <Route element={<PurchaseWrapper />}>
                
                  <Route path="/PurchaseOrder" element={<PurchaseOrder />} />
                 
                </Route> */}
            </Routes>
                
                
    </BrowserRouter>
    </CookiesProvider>
    // </>
  );
}

export default App;
                

