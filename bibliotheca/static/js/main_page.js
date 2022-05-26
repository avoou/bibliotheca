document.addEventListener('DOMContentLoaded', function(){
    let logout = document.querySelector('#logout')
      logout.addEventListener('click', async function (event){
        let response = await fetch("/logout", {
            method: "GET"
        })

        if  (response.ok) {
            let div_mainbox= document.querySelector('div[name=main_box]')
            setTimeout("location.reload()", 500);
            
        } else {
            let div_mainbox= document.querySelector('div[name=main_box]')
            div_mainbox.innerHTML = "whats wrong! Try again"
        }
        })

    let search_button = document.getElementById('search')
    let search_input = document.getElementById('inp')

    search_button.addEventListener('click', async function(event){
      if (search_input.checkValidity()) {           
        let field = document.getElementById('field')
        field.innerHTML = ''

        let response = await fetch(`/search/?search_request=${search_input.value}`, {
          method: "GET"
        })

        const response_json = await response.json()

        if (response.ok) {

          BookEntry = {
            id: '',
            book_json: '',
            authors: '',
            inner_html: '112',
            edit_button_func: function () {
              let book_entry_html = document.getElementById(`book${this.book_json["id"]}`)
              book_entry_html.innerHTML = `
                  <div class="book">
                    <div id="edit_flex">
                      <div name="btn" id="cancel${this.book_json["id"]}" class="edit_button">
                        <h3>x</h3>
                      </div>
                    </div>
                    <input class="add_inp" id="inp_add_title${this.book_json["id"]}" type="text" placeholder="Title of book" maxlength="128" required></br>
                    <input class="add_inp" id="inp_add_authors${this.book_json["id"]}" type="text" placeholder="Authors" maxlength="128" required></br>
                    <input class="add_inp" id="inp_add_description${this.book_json["id"]}" type="text" placeholder="Description" maxlength="1024" required>
                    <div id="submit${this.book_json["id"]}" class="send">Submit</div>
                    <div id="warning${this.book_json["id"]}"></div>
                  </div>`
              let inp_add_title = document.getElementById(`inp_add_title${this.book_json["id"]}`)
              inp_add_title.value = `${this.book_json["title"]}`
              let inp_add_authors = document.getElementById(`inp_add_authors${this.book_json["id"]}`)
              inp_add_authors.value = `${this.authors}`
              let inp_add_description = document.getElementById(`inp_add_description${this.book_json["id"]}`)
              inp_add_description.value = `${this.book_json["description"]}`
              let submit_button = document.getElementById(`submit${this.book_json["id"]}`)
              let cancel_button = document.getElementById(`cancel${this.book_json["id"]}`)
              var self = this

              cancel_button.addEventListener('click', function(){
                book_entry_html.innerHTML = self.inner_html
                let btn = document.getElementById(`edit${self.book_json["id"]}`)
                btn.addEventListener('click', function (){self.edit_button_func()})
              })
              submit_button.addEventListener('click', async function() {
                let authors_list = []
                for (let author of inp_add_authors.value.split(/[;,]/)) {
                  authors_list.push({full_name: author.trimEnd().trimStart()})
                  }
                let response = await fetch("edit", {
                  headers: {'Content-Type': 'application/json'},
                  method: "PUT",
                  body: JSON.stringify({
                    id: self.book_json["id"],
                    title: inp_add_title.value,
                    authors: authors_list,
                    description: inp_add_description.value,
                  })
                })

                const response_json = await response.json()
                if (response.ok) {
                  let warning_message = document.getElementById(`warning${self.book_json["id"]}`)
                  warning_message.style.textAlign = "center"
                  warning_message.innerText = 'The book is edited!'
                  warning_message.style.color = "green"
                } else {
                  let warning_message = document.getElementById(`warning${self.book_json["id"]}`)
                  warning_message.style.textAlign = "center"
                  warning_message.innerText = response_json.detail
                  warning_message.style.color = "red"
                }


              })
            },
            fill_in_inner_html: function () {
              let authors = ''
              for (let index=0; index<this.book_json["authors"].length; index++) {
                this.authors += `${this.book_json["authors"][index].full_name}, `
              }
              this.authors = this.authors.trimEnd().slice(0,-1)
              this.inner_html = `<div id="book${this.book_json["id"]}" class="book">
                                <div id="edit_flex">
                                  <div name="delete_btn" id="delete${this.book_json["id"]}" class="edit_button">
                                    Del
                                  </div>
                                </div>
                                <p>Title: ${this.book_json["title"]}</p>
                                <p>Authors: ${this.authors}</p>
                                <p>Description: ${this.book_json["description"]}</p>
                                <div id="edit_flex">
                                  <div name="btn" id="edit${this.book_json["id"]}" class="edit_button">
                                    Edit
                                  </div>
                                </div>
                                
                                <div id="warning${this.book_json["id"]}"></div>
                                </div>`
            },

            delete_book: async function () {
              let self = this
              let response = await fetch(`book/${this.book_json["id"]}`, {
                  
                  method: "DELETE",
                  
                })
              
                let response_json = await response.json()
                if (response.ok) {
                  let book_entry = document.getElementById(`book${this.book_json["id"]}`)
                  book_entry.innerHTML = 'The book is deleted!'
                } else {
                  let warning_message = document.getElementById(`warning${self.book_json["id"]}`)
                  warning_message.style.textAlign = "center"
                  warning_message.innerText = 'Something wrong!'
                  warning_message.style.color = "red"
                }
            },
          }

          let book_entry_array = []
          for (let book_index=0; book_index<response_json.books.length; book_index++) {
            obj_book_entry = {...BookEntry}
            obj_book_entry.book_json = response_json.books[book_index]
            obj_book_entry.fill_in_inner_html()
            book_entry_array.push(obj_book_entry)
            field.innerHTML += obj_book_entry.inner_html 
          }
          
          /*div_array = document.querySelectorAll("div[name=btn]")
          for (let div_index=0; div_index<div_array.length; div_index++) {
            let btn = div_array[div_index]
            btn.addEventListener('click', function (){book_entry_array[div_index].edit_button_func()})
          }*/

          for (let book_entry of book_entry_array) {
            edit_btn = document.getElementById(`edit${book_entry.book_json["id"]}`)
            edit_btn.addEventListener('click', function (){book_entry.edit_button_func()})
            delete_btn = document.getElementById(`delete${book_entry.book_json["id"]}`)
            delete_btn.addEventListener('click', function (){book_entry.delete_book()})
          }

        } else {
            field.innerHTML += `<div class="book">
            <p>${response_json.detail}</p>
            </div>`
        }
      }
    })

    let add_button = document.getElementById('add')
    add_button.addEventListener('click', function(event){
      let field = document.getElementById('field')
      field.innerHTML = `<div class="book">
        <input class="add_inp" id="inp_add_title" type="text" placeholder="Title of book" maxlength="128" required></br>
        <input class="add_inp" id="inp_add_authors" type="text" placeholder="Authors" maxlength="128" required></br>
        <input class="add_inp" id="inp_add_description" type="text" placeholder="Description" maxlength="1024" required>
        <div id="send" class="send">Send</div>
        <div name="warning"></div>
                        </div>`

        let send_add_button = document.getElementById('send')
        send_add_button.addEventListener('click', async function(event){
            let inp_add_title = document.getElementById('inp_add_title')
            let inp_add_authors = document.getElementById('inp_add_authors')
            let inp_add_description = document.getElementById('inp_add_description')

            if (inp_add_title.checkValidity() && inp_add_authors.checkValidity() && inp_add_description.checkValidity()) {
                let authors_list = []
                for (let author of inp_add_authors.value.split(/[;,]/)) {
                  authors_list.push({full_name: author.trimEnd().trimStart()})
                  }
                
                let response =  await fetch("/add", {
                    headers: {'Content-Type': 'application/json'},
                    method: "POST",
                    body: JSON.stringify({
                        title: inp_add_title.value,
                        authors: authors_list, 
                        description: inp_add_description.value
                    })                 
                })
                let response_json = await response.json()
                console.log("OK: ",response.ok)

                if (response.ok){
                  let warning_message = document.querySelector('div[name=warning]')
                  warning_message.style.textAlign = "center"
                  warning_message.innerText = 'Book added!'
                  warning_message.style.color = "green"
                } else {
                  let warning_message = document.querySelector('div[name=warning]')
                  warning_message.style.textAlign = "center"
                  warning_message.innerText = response_json.detail
                  warning_message.style.color = "red"
                }

            } else {let warning_message = document.querySelector('div[name=warning]')
                    warning_message.style.textAlign = "center"
                    warning_message.innerText = 'All fields must be fill'
                    warning_message.style.color = "red"
                }
        })
    })
})