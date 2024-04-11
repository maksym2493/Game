class MenuTable{
	constructor(){ this.menu = document.querySelector('.menu'); }
	
	open(options = null){ toggle(this.menu, 'table'); }
	close(){ toggle(this.menu); }
	
	async open_game(){
		if(!client.user.game){
			if(client.user.energy.count == 0){ alert('Невистачає енергії.'); return; }
		}

		this.open_next_table(main_game_table);
	}

	async open_next_table(table){
		this.close();
		await table.open();
	}

	async logout(){
		await client.logout();

		this.close();
		await game_table.close();
		await login_table.open();
	}
}