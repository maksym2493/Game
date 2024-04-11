class SettingsTable{
	constructor(){
		this.settings = document.querySelector('.settings');
		this.login = this.settings.querySelector('input[name = "login"]');
		
		this.old_password = this.settings.querySelector('input[name = "old_password"]');
		this.new_password = this.settings.querySelector('input[name = "new_password"]');
		this.repeated_password = this.settings.querySelector('input[name = "repeated_password"]');
	}
	
	clear(){
		this.login.value = '';
		this.clear_password();
	}
	
	update_login(){
		if(this.login.value != client.user.login){ this.login.value = client.user.login; }
	}
	
	clear_password(pos = null){
		if(pos == null || (pos != null && pos == 0)){ this.old_password.value = ''; }
		if(pos == null || (pos != null && pos == 1)){ this.new_password.value = ''; }
		if(pos == null || (pos != null && pos == 2)){ this.repeated_password.value = ''; }
	}
	
	async change_login(){
		const login = this.login.value
		if(login == client.user.login){ alert('Логін вже використовується Вами.'); return }
		
		if(login == null){ alert('Введіть логін'); return }
		if(login.length < 3){ alert('Довжина логіна повинна бути від 3-ох включно символів.'); return }
		
		const result = await client.change_login(login);
		if(result.error == null){ client.user.login = login; game_table.update_login(); alert('Логін змінено.'); }
		else if(result.need_login){
			await close_all();
		}
	}

	async close_all(){
		this.close();
		await game_table.close();
		await login_table.open();
	}
	
	async change_password(){
		var old_password = this.old_password.value
		var new_password = this.new_password.value
		var repeated_password = this.repeated_password.value
		
		if(old_password == ''){ alert('Поточний пароль відсутній.'); return }
		
		if(old_password.length < 6){ alert('Довжина поточного пароля повинна бути від 6-ти включно символів.'); return }
		if(old_password == new_password){ alert('Новий пароль співпадає з поточним.'); return }
		
		if(new_password == ''){ alert('Новий пароль відсутній.'); return }
		
		if(new_password.length < 6){ alert('Довжина нового пароля повинна бути від 6-ти включно символів.'); return }
		
		if(repeated_password == ''){ alert('Повтор нового пароля відсутнє.'); return }
		if(new_password != repeated_password){ alert('Новий пароль не співпадає з повтором.'); return }
		
		const result = await client.change_password(old_password, new_password, repeated_password);
		if(result.error == null){ alert('Пароль успішно змінений.'); this.clear_password(); }
		else if(result.need_login){
			await close_all();
		}
		else{
			if(result.error == 'Forbidden 403'){ this.clear_password(); }
			else{ this.clear_password(0); }
		}
	}
	
	async reset_sessions(){
		const result = await client.reset_sessions();
		if(result.error == null){ alert('Тепер це єдиний пристрій, у якого є доступ до цього аккаунту.'); }
		else if(result.need_login){
			await close_all();
		}
	}

	async back(){
		this.close();
		await menu_table.open();
	};
	
	open(_options = null){ toggle(this.settings, 'table'); this.update_login(); }
	close(){ toggle(this.settings); this.clear(); }
}