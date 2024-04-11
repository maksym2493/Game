class GameTable{
	constructor(){
		this.check_id = null;
		this.cur_time = new Date().getTime().toString();
		
		localStorage.setItem('online', this.cur_time);
		
		this.timeout_id = null;
		this.interval_id = null;
		this.start_interval_time = null;
		this.game = document.querySelector('.top_bar');
		
		this.login = this.game.querySelector('span[id = "login"]');
		this.energy = this.game.querySelector('span[id = "energy"]');

		this.energy_timer_tr = this.game.querySelector('#energy_timer_tr');
		this.energy_timer = this.energy_timer_tr.querySelector('#energy_timer');
	}
	
	async update_top_bar(){
		if(client.user == null){
			const res = await client.get_profile(null, true);

			if(res.error != null){
				return res;
			}
		}
		
		this.update_login();
		this.energy.innerHTML = client.user.energy.count;
	}
	
	update_login(){ this.login.innerHTML = client.user.login + '.'; }
	
	clear(){
		this.login.innerHTML = '';
		this.energy.innerHTML = '';
	}
	
	async open(options = null){
		const res = await this.update_top_bar();

		if(res != null){
			login_table.open();
			return;
		}
		
		toggle(this.game, 'table');
		this.check_id = setInterval(this.check.bind(this), 500);
		
		if(client.user.game != null){ main_game_table.load(); }
		if(client.user.energy.time != null){ this.start_interval(false); }

		menu_table.open();
	}
	
	async close(){
		this.check_id = null;
		clearInterval(this.check_id);
		if(this.timeout_id){ clearTimeout(this.timeout_id); }
		
		if(this.interval_id){ this.stop_interval(); }
		if(client.user.game != null){ main_game_table.stop_interval(); }
		
		toggle(this.game); this.clear();
	}

	start_interval(min = true){
		if(min){
			client.user.energy.count -= 1;
			this.energy.innerHTML = client.user.energy.count;
		}

		if(this.interval_id == null){
			this.start_interval_time = client.user.energy.time
			if(this.start_interval_time == null){ this.start_interval_time = new Date().getTime(); }
			else{ this.start_interval_time *= 1000; }

			this.energy_timer_tr.style.display = 'table-cell';
			this.energy_timer.innerHTML = get_time_delta(Math.floor(this.start_interval_time / 1000), Math.floor((new Date().getTime()) / 1000), 3600);

			this.update_energy();
			const delay = 1000 - new Date().getMilliseconds();
			this.timeout_id = setTimeout(() => {
				this.timeout_id = null;
				this.interval_id = setInterval(this.update_energy.bind(this), 1000);

				this.update_energy();
			}, delay);
		}
	}

	check(){
		if(localStorage.getItem('online') != this.cur_time){
			clearInterval(this.check_id);
			confirm('Відкрита нова вкладка...');

			location.reload();
			return;
		}
	}

	stop_interval(){
		clearInterval(this.interval_id);
		
		this.interval_id = null;
		this.start_interval_time = null;

		this.energy_timer.innerHTML = '';
		this.energy_timer_tr.style.display = 'none';
	}

	update_energy(){
		let cur_time = new Date().getTime();
		while(cur_time - this.start_interval_time >= 3600000){
			client.user.energy.count += 1;
			this.energy.innerHTML = client.user.energy.count;

			if(client.user.energy.count == 10){ this.stop_interval(); return; } else{ this.start_interval_time += 3600000; }
		}

		this.energy_timer.innerHTML = get_time_delta(Math.floor(this.start_interval_time / 1000), Math.floor(cur_time / 1000), 3600);
	}
}