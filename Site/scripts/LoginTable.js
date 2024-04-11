class LoginTable{
	constructor(){
		this.login_table = document.querySelector('.login_table')
		
		this.l = this.login_table.querySelector('input[name = "login"]');
		this.p = this.login_table.querySelector('input[name = "password"]');
	}
	
	async login(){
		const login = this.l.value;
		const password = this.p.value;
		
		if(login == ''){ alert('Введіть логін.'); return }
		if(login.length < 3){ alert('Довжина логіна повинна бути від 3-ох включно символів.'); return }
		
		if(password == ''){ alert('Введіть пароль.'); return }
		if(password.length < 6){ alert('Довжина паролю повинна бути від 6-ти включно символів.'); return }
		
		const result = await client.login(login, password);
		console.log('LoginTable', result);
		
		if(result.error == null){
			this.close();
			await game_table.open();
		
		} else if(result.error == 'Невірний пароль.'){ this.p.value = ''; }
		else if(result.error == 'Forbidden 403'){ this.l.value = ''; this.p.value = ''; }
	}
	
	open(options = null){ toggle(this.login_table, 'table'); }
	close(){ toggle(this.login_table); this.l.value = ''; this.p.value = ''; }
}