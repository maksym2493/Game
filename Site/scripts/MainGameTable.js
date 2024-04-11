const max_cells = 25;

class MainGameTable{
    constructor(){
        this.scale = null;
        this.timeout_id = null;
        this.interval_id = null;
        this.storage = new Storage('main_game_table_scale');

        this.action = null;
        this.game_data = null;

        this.game = document.querySelector('.main_game_table');
        this.game_container = this.game.querySelector('#game_container');

        this.game_timer = this.game.querySelector('#game_timer');
        this.game_score = this.game.querySelector('#game_score');

        this.buttons = [this.game.querySelector('#button_1'), this.game.querySelector('#button_2')];

        this.click_listener = this.make_action.bind(this);
        this.scrolling_listener = this.scrolling.bind(this);
    }

    async open(options = null){
        if(this.scale == null){
            this.scale = 0
            const loaded_scale = parseFloat(this.storage.load(0));
            if(loaded_scale != 0){ this.scale_game(loaded_scale); }
        }

        if(client.user.game == null){
            this.game_container.scrollTop = 0;
            this.game_container.scrollLeft = 0;
            
            const data = await client.start_game();
            
            if(data.error != null){
                if(data.need_login){
                    await this.close_all();
                }
                
                return;
            }

            game_table.start_interval();
            
            client.user.game = data;
            this.load();
        
        } else{ this.change_action(0); }

        toggle(this.game, 'table');
        this.game_container.addEventListener('wheel', this.scrolling_listener);
    }

    async close_all(){
        this.close();
        await game_table.close();
        await login_table.open();
    }

    load(){
        console.log('Loaded');
        this.game_data = client.user.game;
    
        this.gen_table();
        this.game_data.start_time *= 1000;
        
        console.log('Marked', this.game_data.marked);
        this.update_game(this.game_data.opened, this.game_data.marked);
        
        this.playing();
        const delay = 1000 - new Date().getMilliseconds();
		this.timeout_id = setTimeout(() => {
			this.timeout_id = null;
			this.interval_id = setInterval(this.playing.bind(this), 1000);

			this.playing();
		}, delay);
    }

    gen_table(){
        this.change_action(0);

        for(let i = 0; i < max_cells; i++){
            for(let j = 0; j < max_cells; j++){
                const new_element = document.createElement('div');
                
                new_element.id = `cell_${i}_${j}`;
                this.game_container.appendChild(new_element);
                new_element.addEventListener('click', this.click_listener);
            }
        }
    }

    scrolling(event){
        const shift = event.shiftKey;
        const ctrl = event.ctrlKey;
        
        const x = event.deltaX * 0.3;
        const y = event.deltaY * 0.3;

        if(ctrl){ this.scale_game(-y * 0.3, event.clientX, event.clientY); }
        else{
            if(shift){
                this.game_container.scrollLeft += y;
                this.game_container.scrollTop += x;
            
            } else{
                this.game_container.scrollLeft += x;
                this.game_container.scrollTop += y;
            }
        }
        
        event.preventDefault();
    }

    async playing(){
        console.log('Playing', 1);
        let cur_time = new Date().getTime();
        if(cur_time - this.game_data.start_time >= 3600000){ await this.end_game(1); return; }

        this.update_game();
    }

    update_game(opened = null, marked = null){
        if(opened){
            for(let cell in opened){
                cell = opened[cell];
                let element = this.game_container.querySelector(`#cell_${cell.pos[0]}_${cell.pos[1]}`);
                
                if(cell.count != 0){
                    element.innerHTML = cell.count;
                    element.style.backgroundColor = 'white';
                    element.style.border = '3px solid black';
                
                } else{ element.style.backgroundColor = 'brown'; }

                element.style.cursor = 'auto';
                element.removeEventListener('click', this.click_listener);
            }
        }

        if(marked){
            for(let cell in marked){
                cell = marked[cell];
                let element = this.game_container.querySelector(`#cell_${cell[0]}_${cell[1]}`);
                
                element.style.backgroundColor = 'black';
            }
        }

        this.game_score.innerHTML = this.game_data.score;
        this.game_timer.innerHTML = get_time_delta(Math.floor(this.game_data.start_time / 1000), Math.floor(new Date().getTime() / 1000), 3600);
    }

    change_action(action){
        if(action == this.action){ return; }
        
        console.log(this.buttons[action]);
        if(this.action != null){ this.buttons[this.action].style.border = ''; }
        
        this.buttons[action].style.border = '5px solid green';
        this.action = action;
    }

    async make_action(event){
        const element = event.currentTarget;
        const splited_id = element.id.split('_');

        const i = parseInt(splited_id[1]);
        const j = parseInt(splited_id[2]);
        
        if(this.action == 0){
            if(this.game_data.marked.findIndex(item => item[0] === i && item[1] === j) != -1){ if(!confirm('Ця клітинка відмічена. Ви впевнені, що хочете її відкрити?')){ return; } }
            
            let win = false;
            let updates = await client.open_cell(i, j);

            if(updates.error != null){
                if(updates.need_login){
                    await this.close_all();
                }
                
                return;
            }
            
            if(updates.end){ await this.end_game(); return; }
            if(updates.win){ this.game_data.score = updates.score; await this.end_game(2); return; }
            
            this.game_data.score += updates.length;
            this.update_game(updates);
        }
        else{
            const cell = [i, j];
            const res = await client.mark_cell(i, j);
            if(res.error != null){
                if(res.need_login){
                    await this.close_all();
                }

                return;
            }
            
            let color = 'black';
            
            let index = this.game_data.marked.findIndex(item => item[0] === cell[0] && item[1] === cell[1]);
            if(index !== -1){ this.game_data.marked.splice(index, 1); color = 'green'; }
            else{ this.game_data.marked.push(cell); }

            element.style.backgroundColor = color;
        }
    }

	scale_game(scale, left = null, top = null){
        const old_scale = this.scale;

        const game_container = this.game_container.getBoundingClientRect();
        if(left == null){ left = game_container.left + this.game_container.offsetWidth / 2; top = game_container.top + this.game_container.offsetHeight / 2; }
        
        const hovered_element = document.elementFromPoint(left, top);
        const before_hovered_element_rect = hovered_element.getBoundingClientRect();
                
        const top_before = before_hovered_element_rect.top - game_container.top;
        const left_before = before_hovered_element_rect.left - game_container.left;

        this.scale += scale;
        if(this.scale > 60){ this.scale = 60; }
        if(this.scale < -70){ this.scale = -70; }
        
        this.game_container.style.fontSize = `${(100 + this.scale) / 2}px`;
        this.game_container.style.gridTemplateRows = `repeat(25, ${100 + this.scale}px)`;
        this.game_container.style.gridTemplateColumns = `repeat(25, ${100 + this.scale}px)`;

        if(old_scale != this.scale){
            this.storage.save(this.scale);
            
            const after_hovered_element_rect = hovered_element.getBoundingClientRect();
            
            const top_after = after_hovered_element_rect.top - game_container.top;
            const left_after = after_hovered_element_rect.left - game_container.left;

            this.game_container.scrollTop += top_after - top_before;
            this.game_container.scrollLeft += left_after - left_before;
        }
	}

    async end_game(end = 0){
        client.user.game = null;
        client.user.season_score += this.game_data.score;
        
        let m = 'Це міна!';
        if(end == 1){ m = 'Час вийшов!'; }
        else if(end == 2){ m = 'Перемога!'; }
        
        alert(`${m} Гра завершена.\nЗароблено балів: ${this.game_data.score}.`);

        client.user.level.exp[0] += this.game_data.score;
        while(client.user.level.exp[0] >= client.user.level.exp[1]){
            client.user.level.exp[0] -= client.user.level.exp[1];

            client.user.level.level += 1;
            client.user.level.exp[1] += 100;

            alert(`Досягнутий ${client.user.level.level}-ий рівень!`);
        }

        this.game_container.innerHTML = '';

        this.action = null;
        this.game_data = null;

        this.game_timer.innerHTML = '';
        this.game_score.innerHTML = '';

        this.stop_interval();
        if(this.game.style.display != 'none'){
            if(client.user.energy.count != 0 && confirm('Бажаєте спробувати ще раз?')){ this.open(); return; }
            await this.back();
        }
    }

    stop_interval(){
        if(this.timeout_id != null){
            clearTimeout(this.timeout_id);
            this.timeout_id = null;
        }

        if(this.interval_id != null){
            clearInterval(this.interval_id);
            this.interval_id = null;
        }
    }

    close(){
        toggle(this.game); this.game_container.removeEventListener('wheel', this.scrolling_listener);
    }

    async back(){
        this.close();
        await menu_table.open();
    }
}