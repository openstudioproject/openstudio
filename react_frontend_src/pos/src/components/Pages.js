import React, { Component } from "react"
import PageTemplate from "./PageTemplate"


export class POS extends Component {
    constructor(props) {
        super(props)
    }

    render() {
        return (
            <PageTemplate>
            <section className="POS">
                <div>POS</div>
            </section>
            </PageTemplate>
        )
    }
}

export class Welcome extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    setLoaderStatus(status) {
        this.props.setLoaderStatus(status)
    }

    componentWillMount() {
        this.setLoaderStatus('loading')
    }

    componentDidMount() {
        // setTimeout(function() {console.log('done loading...')}, 2000)
        setTimeout(() => this.setLoaderStatus('ready'), 1500)
    }

    render() {
        console.log('Welcome here')
        return (this.props.loader.status === 'loading') ?
            <div>Loading...</div> :
            <PageTemplate>
            <section className="Welcome">
                <div>Welcome page</div>
                <div>{this.props.loader.status}</div>
                <div>{this.props.loader.message}</div>
            </section>
            </PageTemplate>
    }
}


export const Whoops404 = ({ location }) =>
    <div className='whoops-404'>
        <h1>Resource not found at '{location.pathname}'</h1>
    </div>
