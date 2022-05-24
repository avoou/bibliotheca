document.addEventListener('DOMContentLoaded', function(){
    let registration_button = document.getElementById("registrtion_button")
    registration_button.addEventListener('click', function(event){
        document.location.href = "/registration";
    })    

    let form_button = document.querySelector('input[type=submit]')
    form_button.addEventListener('click', async function (event){
        //event.preventDefault();
        let all_inputs = document.querySelectorAll("input[class=text_input]")
        console.log(all_inputs[0].checkValidity())
        console.log(all_inputs[1].checkValidity())
        let input_username = all_inputs[0]
        let input_password = all_inputs[1]
        if (input_username.checkValidity() && input_password.checkValidity()) {
            event.preventDefault();
            let response = await fetch("/login", {
                headers: {'Content-Type': 'application/json'},
                method: "POST",
                body: JSON.stringify({email: input_username.value, password: input_password.value})
                });

            let response_json = await response.json()

            if  (response.ok) {
                let div_mainbox= document.querySelector('div[name=main_box]')
                div_mainbox.innerHTML = `<div name="message">
                                            Hello, 
                                                <h3 style="display: inline-block;">
                                                    <div name="user_name" style="display: inline-block;"></div>!
                                                </h3>
                                            </br>
                                            You are successfully logged in)))</br>
                                            Loading ...
                                        </div>`
                let username = div_mainbox.querySelector('div[name=user_name]')
                username.innerText = response_json.username
                setTimeout(function(){document.location.href = "/"}, 1500);  
                } else {
                let warning_message = document.querySelector('div[name=auth_false_warning]')
                warning_message.style.textAlign = "center"
                warning_message.innerText = response_json.detail /*"Wrong data!"*/
                warning_message.style.color = "red"
            }
        } 
    }) 
})