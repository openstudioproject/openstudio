import React, { Component } from "react"
import { render } from "react-dom"

import PageTemplate from "./PageTemplate"

export const POS = () =>
    <PageTemplate>
        <section className = "POS">
            <div>POS</div>
        </section>
    </PageTemplate>


export const Whoops404 = ({ location }) =>
    <div className='whoops-404'>
        <h1>Resource not found at '{location.pathname}'</h1>
    </div>