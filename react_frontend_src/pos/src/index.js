import React from 'react'
import ReactDOM from 'react-dom'
import { Provider } from 'react-redux'
import { addLocaleData } from 'react-intl'
import storeFactory from './store'
import en from 'react-intl/locale-data/en'
import App from './app/App'
import ConnectedIntlProvider from './ConnectedIntlProvider'

const store = storeFactory()
console.log(store.getState())

// addLocaleData([...en, ...nl]) for example to add Dutch
console.log(en)
addLocaleData([...en])

ReactDOM.render(
  <Provider store={store}>
      <ConnectedIntlProvider>
        <App />
      </ConnectedIntlProvider>
  </Provider>,
  document.getElementById("app")
)