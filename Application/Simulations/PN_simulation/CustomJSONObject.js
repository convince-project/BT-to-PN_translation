class CustomJSONObject {
  constructor() {
    this.dataObjects = new Map();
    this.dataFloats = new Map();
    this.dataStrings = new Map();
    this.dataArray = new Map();
    this.dataBoolean = new Map();
  }

  setString(k, value) {
    this.dataStrings.set(k, value);
  }

  setFloat(k, value) {
    this.dataFloats.set(k, value);
  }

  setJSONObject(k, value) {
    this.dataObjects.set(k, value);
  }

  setJSONArray(k, value) {
    this.dataArray.set(k, value);
  }

  setBoolean(k, value) {
    this.dataBoolean.set(k, value);
  }

  getString(k) {
    return this.dataStrings.get(k);
  }

  getFloat(k) {
    return this.dataFloats.get(k);
  }

  getJSONObject(k) {
    return this.dataObjects.get(k);
  }

  getJSONArray(k) {
    return this.dataArray.get(k);
  }

  getBoolean(k) {
    return this.dataBoolean.get(k);
  }
}

class CustomJSONArray {
  constructor() {
    this.data = [];
  }

  add(value) {
    this.data.push(value);
  }

  size() {
    return this.data.length;
  }

  get(index) {
    return this.data[index];
  }

  toJSON() {
    let json = "[";

    for (const value of this.data) {
      if (typeof value === "string" || value instanceof String || typeof value === "char") {
        json += `"${value}",`;
      } else {
        json += `${value},`;
      }
    }

    if (json.length > 1) {
      json = json.slice(0, -1); // Remove the trailing comma
    }

    json += "]";

    return json;
  }
}
