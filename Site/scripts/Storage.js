class Storage{
	constructor(name){ this.name = name; }
	remove(){ return localStorage.removeItem(this.name); }
	load(def = null){ return localStorage.getItem(this.name) || def; }
	save(element){ console.log(this.name, element, 'saving...'); localStorage.setItem(this.name, element); }
}