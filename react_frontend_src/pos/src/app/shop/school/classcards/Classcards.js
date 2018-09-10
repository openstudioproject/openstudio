import React, { Component } from "react"
import { intlShape } from "react-intl"
import PropTypes from "prop-types"

import ShopTemplate from '../../components/ShopTemplate'

import ClasscardsList from './ClasscardsList'

class Classcards extends Component {
    constructor(props) {
        super(props)
        console.log(props)
    }

    PropTypes = {
        intl: intlShape.isRequired,
        setPageTitle: PropTypes.function,
        app: PropTypes.object,
        classcards: PropTypes.object,
        loaded: PropTypes.boolean,
    }

    componentWillMount() {
        this.props.setPageTitle(
            this.props.intl.formatMessage({ id: 'app.pos.products' })
        )
    }
    
    render() {
        return (
            <ShopTemplate app_state={this.props.app}>
                { this.props.loaded ? 
                     <ClasscardsList classcards={this.props.classcards} /> :
                     "Loading..."
                }
            </ShopTemplate>
        )
    }
}

export default Classcards
