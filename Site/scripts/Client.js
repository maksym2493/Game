class Client{
	constructor(){
		this.last_timeout_id = null;
		this.loading = document.querySelector('.loading');
		this.loading_image = this.loading.querySelector('img');

		this.user = null;
		this.device_id = localStorage.getItem('device_id');

		if(this.device_id != null && localStorage.getItem('need_auth') == null){
			localStorage.setItem('need_auth', false);
		}
	}

	//Parser  
	async parse_result(result){
		if(result.status == 'OK'){ return result.result || result; }
		else{
			result.need_login = this.parse_error(result.error);
			
			return result;
		}
	}

	parse_error(error){
		if(error == 403){ location.reload(); return; }
		if(error == 'Необхідна авторизація.'){
			localStorage.setItem('need_auth', true);
			
			alert(error); return true;
		}

		if(error == 'Необхідне перезавантаження.'){
			let userAnswer = confirm("На Ваш аккаунт хтось заходив. Необхідне оновлення даних.\nПідтвердьте, в іншому випадку перейдете на меню логіну.");

			if(!userAnswer){
				return true;
			}

			location.reload();

			return;
		}
	
		alert(error);
	}

	edit_loading(action = 1){
		this.loading.style.display = ['none', 'block'][action];
		this.loading.style.pointerEvents = ['none', 'auto'][action];

		if(action == 1){ this.last_timeout_id = setTimeout(() => { this.loading_image.style.display = 'inline-block'; }, 1_000); }
		else{ clearTimeout(this.last_timeout_id); this.loading_image.style.display = 'none'; }
	}

	async login(login, password){
		this.edit_loading();

		const params = {
			login: login,
			password: password,
		};

		if(this.device_id != null){
			params['device_id'] = this.device_id;
		}
		
		const response = await fetch(`/api/login?` + new URLSearchParams(params));
		const data = await response.json();

		if(data.status == 'OK'){
			this.user = data.result.user;
			this.device_id = data.result.device_id;
			localStorage.setItem('need_auth', false);
			localStorage.setItem('device_id', this.device_id);
		}
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
	
	async get_profile(user_id = null, first_time = false){
		this.edit_loading();
		
		const params = { device_id: this.device_id }
		if(user_id != null){ params.user_id = user_id; }
		
		if(first_time){
			params.first_time = true;
		}
		
		const response = await fetch(`/api/get_profile?` + new URLSearchParams(params));
		const data = await response.json();

		if(user_id == null && data.status == 'OK'){
			this.user = data.result;
			check_notifications();
		}
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
	
	async logout(){
		this.edit_loading();

		const params = { device_id: this.device_id };
		const response = await fetch(`/api/logout?` + new URLSearchParams(params));
		
		const data = await response.json();
		localStorage.setItem('need_auth', true);
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
		
	async change_login(login){
		this.edit_loading();

		const params = {
			device_id: this.device_id,
			login: login
		}

		const response = await fetch(`/api/change_login?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
	
	async change_password(old_password, new_password, repeated_password){
		this.edit_loading();

		const params = {
			device_id: this.device_id,
			old_password: old_password,
			new_password: new_password,
			repeated_password: repeated_password
		};

		const response = await fetch(`/api/change_password?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
	
	async reset_sessions(){
		this.edit_loading();

		const params = { device_id: this.device_id }
		const response = await fetch(`/api/reset_sessions?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}

	//Main Game
	async start_game(){
		this.edit_loading();
		
		const params = { device_id: this.device_id }
		const response = await fetch(`/api/start_game?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}

	async open_cell(i, j){
		this.edit_loading();
		
		const params = {
			device_id: this.device_id,
			i: i,
			j: j
		}
		
		const response = await fetch(`/api/open_cell?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}

	async mark_cell(i, j){
		this.edit_loading();

		const params = {
			device_id: this.device_id,
			i: i,
			j: j
		}

		const response = await fetch(`/api/mark_cell?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}

	//Tops
	async get_season_top(page){
		this.edit_loading();
		
		const params = { device_id: this.device_id }
		if(page != null){ params.page = page; }
		
		const response = await fetch(`/api/get_season_top?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}

	async get_global_top(page){
		this.edit_loading();
		
		const params = { device_id: this.device_id }
		if(page != null){ params.page = page; }
		
		const response = await fetch(`/api/get_global_top?` + new URLSearchParams(params));
		const data = await response.json();
		
		this.edit_loading(0);
		return await this.parse_result(data);
	}
}