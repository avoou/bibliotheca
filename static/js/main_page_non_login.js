document.addEventListener('DOMContentLoaded', function(){
    let login = document.querySelector('#login')
      login.addEventListener('click', async function (event){
          document.location.href = "/login";
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
            inner_html: '',
            
            fill_in_inner_html: function () {
              let authors = ''
              for (let index=0; index<this.book_json["authors"].length; index++) {
                this.authors += `${this.book_json["authors"][index].full_name}, `
              }
              this.authors = this.authors.trimEnd().slice(0,-1)
              this.inner_html = `<div id="book${this.book_json["id"]}" class="book">
                                <p>Title: ${this.book_json["title"]}</p>
                                <p>Authors: ${this.authors}</p>
                                <p>Description: ${this.book_json["description"]}</p>
                                </div>`
            },
          }

          for (let book_index=0; book_index<response_json.books.length; book_index++) {
            obj_book_entry = {...BookEntry}
            obj_book_entry.book_json = response_json.books[book_index]
            obj_book_entry.fill_in_inner_html()
            field.innerHTML += obj_book_entry.inner_html 
          }
        } else {
            field.innerHTML += `<div class="book">
            <p>${response_json.detail}</p>
            </div>`
        }
      }
    })       
})