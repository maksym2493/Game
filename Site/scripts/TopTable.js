class TopTable{
    constructor(){
        this.cur_type = 0;
        this.page_changed = false;
        this.table = document.querySelector('.top');

        this.headers = this.table.querySelector('#headers');
        this.headers_buttons = [this.headers.querySelector('#season_top'), this.headers.querySelector('#global_top')];

        this.page_number = this.table.querySelector('#page_number');
        this.top_container = this.table.querySelector('#top_container');
        
        this.listener = this.listener.bind(this);
        this.tops = {season_top: null, global_top: null};
        this.tops_metas = {season_top: null, global_top: null};

        this.menu = this.table.querySelector('#top_menu');
        this.back_button = this.menu.querySelector('#back');
        this.next_button = this.menu.querySelector('#next');

        this.end_of_season = null;
        this.end_of_season_timeout_id = null;
        this.end_of_season_interval_id = null;
        this.end_of_season_span = this.table.querySelector('#end_of_season_span');

        this.profile_is_opened = false;
    }

    async listener(event){
        const user_id = event.currentTarget.id.split('_')[1];
        
        this.profile_is_opened = true;

        this.close();
        await profile_table.open(user_id);
    }

    unregister(){
        const elements = this.top_container.querySelectorAll('div');
        for(let element of elements){ element.removeEventListener('click', this.listener); }
    }

    update_season(){
        if(this.table.style.display == 'table-row'){
            this.tops.season_top = null; this.tops.global_top = null;
            this.open({profile: true});
        }
    }

    async update(page_adder = 0){
        const key = ['season_top', 'global_top'][this.cur_type];

        if(page_adder == 0){
            if(this.page_changed){ await this.load(key, this.cur_type, this.tops_metas[key].page); }
            else{ await this.load(key, this.cur_type); }
        }
        else{
            window.scrollTo({
                top: 0,
                left: 0,
                behavior: 'smooth',
            });
            
            this.page_changed = true;
            await this.load(key, this.cur_type, this.tops_metas[key].page + page_adder);
        }
        
        this.top_container.innerHTML = ''; this.gen_top(key);
    }

    async change_state(type, check_errors = false){
        this.headers_buttons[type].style.cursor = 'auto';
        window.getComputedStyle(this.headers_buttons[type]).getPropertyValue('cursor');
        
        this.headers_buttons[type].style.pointerEvents = 'none';
        this.headers_buttons[type].style.backgroundColor = 'green';
        
        this.headers_buttons[(type + 1) % 2].style.cursor = 'pointer';
        this.headers_buttons[(type + 1) % 2].style.pointerEvents = 'auto';
        this.headers_buttons[(type + 1) % 2].style.backgroundColor = 'white';
        
        this.cur_type = type;

        const res = await this.open_top(type);

        if(check_errors){
            if(res != null && res.error != null){
                if(res.need_login){
                    await this.close_all();
                }
                
                return;
            }

            return;
        }

        return res;
    }

    async open_top(type, page = null){
        this.top_container.innerHTML = '';
        const key = ['season_top', 'global_top'][type];
        if(this.tops[key] == null){
            const res = await this.load(key, type, page);
            
            if(res != null){
                return res;
            }

            this.gen_top(key);
        }
        else{
            this.page_number.innerHTML = this.tops_metas[key].page;
            this.update_buttons(this.tops_metas[key]);
            this.gen_top(key);
        }
    }

    gen_top(key){
        for(let element of this.tops[key]){ this.add_div(element); }
    }

    async load(key, type, page = null){
        let answer = null;

        if(type == 0){ answer = await client.get_season_top(page); }
        else{ answer = await client.get_global_top(page); }
        
        if(answer.error != null){
            if(answer.error == 'Сторінка не знайдена.'){
                return this.load(key, type);
            }
            
            return answer;
        }
        
        this.tops[key] = answer.top;
        this.end_of_season = answer.end_of_season;

        let meta = this.tops_metas[key];
        if(meta == null){ meta = {length: 0, page: 0}; this.tops_metas[key] = meta; }
        
        meta.page = answer.page;
        meta.length = answer.length;
        this.page_number.innerHTML = meta.page;

        this.update_buttons(meta);
    }

    update_buttons(meta){
        if(meta.page == 1){ this.back_button.style.visibility = 'hidden'; }
        else{ this.back_button.style.visibility = 'visible'; }
        
        length = Math.floor(meta.length / 5);
        if(meta.length != 0 && meta.length % 5 == 0){ length -= 1; }
        if(length + 1 == meta.page){ this.next_button.style.visibility = 'hidden'; }
        else{ this.next_button.style.visibility = 'visible'; }
    }

    add_div(data){
        const names = ['pos', 'login', 'score'];
        const div = document.createElement('div');
        
        for(let i = 0; i < 3; i++){
            const name = names[i];
            const span = document.createElement('span');
            
            if(i != 1){ span.innerHTML = transform_digit(data[name]); }
            else{ span.innerHTML = data[name]; }

            span.id = name;
            div.appendChild(span);
        }

        div.id = `id_${data.user_id}`;
        if(data.user_id == client.user.user_id){ div.style.backgroundColor = 'green'; div.style.cursor = 'auto'; }
        else{ div.addEventListener('click', this.listener); }
        
        this.top_container.appendChild(div);
    }

    update_end_of_season(){
        const cur_time = Math.floor((new Date().getTime()) / 1000)
        if(cur_time > this.end_of_season){
            this.end_of_season_span.innerHTML = 'Сезон завершений.';
            clearInterval(this.end_of_season_interval_id);
            
            return;
        }
        
        this.end_of_season_span.innerHTML = get_time_delta(cur_time, this.end_of_season);
        
        if(this.end_of_season_interval_id == null){
            const delay = 1000 - new Date().getMilliseconds();
			this.end_of_season_timeout_id = setTimeout(() => {
                this.end_of_season_timeout_id = null;
				this.end_of_season_interval_id = setInterval(this.update_end_of_season.bind(this), 1000);

                this.update_end_of_season();
			}, delay);
        }
    }

    async open(){
        const res = await this.change_state(this.cur_type);
        
        if(res != null && res.error != null){
            if(res.need_login){
                await this.close_all();
            }
            
            return;
        }

        this.update_end_of_season();
        toggle(this.table, 'table');
    }

    async close_all(){
        this.close();
        await game_table.close();
        await login_table.open();
    }

    async back(){
        this.cur_type = 0;
        this.page_changed = false;
        this.tops.season_top = null;
        this.tops.global_top = null;

        this.close();
        await menu_table.open();
    }

    close(){
        if(this.end_of_season_timeout_id){
            clearTimeout(this.end_of_season_timeout_id);
        }

        if(this.end_of_season_interval_id){
            clearInterval(this.end_of_season_interval_id);
            this.end_of_season_span.innerHTML = '';
            this.end_of_season_interval_id = null;
        }

        this.unregister();
        this.top_container.innerHTML = '';
        toggle(this.table);
    }
}